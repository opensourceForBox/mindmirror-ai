"""心理测评 API 路由

提供量表查询、提交评分、历史记录等端点。
"""
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.scales import get_scale, list_scales
from src.models.assessment import Assessment
from src.models.database import get_db
from src.models.user import User
from src.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assessment", tags=["心理测评"])


# ─── 请求/响应模型 ─────────────────────────────────────────────────────────────

class ScaleBrief(BaseModel):
    scale_type: str
    name: str
    title: str
    description: str
    category: str
    question_count: int
    estimated_minutes: int


class ScaleOption(BaseModel):
    label: str
    value: int


class ScaleQuestion(BaseModel):
    id: int
    text: str


class ScaleDetail(BaseModel):
    scale_type: str
    name: str
    title: str
    description: str
    category: str
    questions: list[ScaleQuestion]
    options: list[ScaleOption]
    reverse_items: list[int]


class AssessmentSubmitRequest(BaseModel):
    scale_type: str = Field(..., description="量表类型，如 phq9/gad7/pss10/sds")
    answers: list[int] = Field(..., description="每题选项值组成的数组")


class AssessmentResult(BaseModel):
    score: int = Field(..., description="最终得分（SDS 为标准分）")
    raw_score: int | None = Field(None, description="原始总分（仅 SDS 有区分）")
    interpretation: str
    level: str
    suggestions: list[str]
    scale_type: str
    created_at: str | None = None


class AssessmentHistoryItem(BaseModel):
    id: int
    scale_type: str
    scale_name: str
    total_score: int
    interpretation: str | None
    created_at: str


class AssessmentHistoryResponse(BaseModel):
    total: int
    items: list[AssessmentHistoryItem]
    page: int
    page_size: int


class AssessmentDetailResponse(BaseModel):
    id: int
    scale_type: str
    scale_name: str
    answers: list[int]
    total_score: int
    interpretation: str | None
    created_at: str


# ─── 评分逻辑 ──────────────────────────────────────────────────────────────────

CRISIS_SUGGESTIONS = [
    "你提到的念头非常重要，请立即联系信任的人或专业危机干预热线。",
    "如果伤害自己的想法变强烈，请拨打 24 小时危机干预热线：400-161-9995。",
    "你并不孤单，寻求专业帮助是勇敢且正确的选择。",
]

GENERAL_SUGGESTIONS = {
    "none": [
        "状态看起来不错，继续保持规律的作息和适度运动。",
        "可以尝试写感恩日记，巩固积极情绪。",
    ],
    "mild": [
        "留意近期情绪波动，尝试每天留出 10 分钟放松。",
        "与信任的朋友或家人聊聊，倾诉能有效缓解压力。",
        "保持规律睡眠，减少睡前使用电子产品。",
    ],
    "moderate": [
        "建议安排时间进行正念呼吸或轻度运动。",
        "如果情绪持续两周以上，考虑预约学校心理老师或咨询师。",
        "尝试把大任务拆小，减少 overwhelm 感。",
    ],
    "moderately_severe": [
        "建议尽快联系心理健康专业人士进行评估。",
        "在此期间，请让信任的亲友了解你的状态。",
        "避免独处过久，保持基本作息和饮食。",
    ],
    "severe": [
        "建议尽快寻求专业心理或精神科帮助。",
        "请告诉你信任的成年人或朋友你现在的感受。",
        "如果产生自伤/自杀念头，请立即拨打危机干预热线。",
    ],
    "low": [
        "压力水平较低，继续保持良好的生活节奏。",
        "可以尝试培养兴趣爱好，增强心理韧性。",
    ],
    "normal": [
        "抑郁自评结果在正常范围，继续保持。",
        "规律运动和社交有助于维持良好状态。",
    ],
    "high": [
        "压力水平较高，建议学习一些压力管理技巧。",
        "适当减少任务负荷，给自己留出恢复时间。",
        "必要时可寻求心理咨询师的支持。",
    ],
}


def _calculate_score(scale_type: str, answers: list[int]) -> tuple[int, int | None, dict[str, Any]]:
    """计算得分，返回 (最终得分, 原始分, 匹配区间)"""
    scale = get_scale(scale_type)
    if scale is None:
        raise HTTPException(status_code=400, detail=f"不支持的量表类型: {scale_type}")

    expected = len(scale["questions"])
    if len(answers) != expected:
        raise HTTPException(
            status_code=400,
            detail=f"答案数量不匹配: 期望 {expected} 题，实际 {len(answers)} 题",
        )

    reverse_items = set(scale.get("reverse_items", []))
    options = scale["options"]
    min_value = min(opt["value"] for opt in options)
    max_value = max(opt["value"] for opt in options)

    raw_scores: list[int] = []
    for idx, answer in enumerate(answers, start=1):
        valid_values = [opt["value"] for opt in options]
        if answer not in valid_values:
            raise HTTPException(
                status_code=400,
                detail=f"第 {idx} 题答案值 {answer} 不在允许范围 {valid_values} 内",
            )
        if idx in reverse_items:
            raw_scores.append(max_value + min_value - answer)
        else:
            raw_scores.append(answer)

    raw_total = sum(raw_scores)

    scoring_rules = scale["scoring_rules"]
    multiplier = scoring_rules.get("standard_score_multiplier")
    if multiplier:
        final_score = int(round(raw_total * multiplier))
    else:
        final_score = raw_total
        raw_total = None  # type: ignore[assignment]

    matched = None
    for rule in scoring_rules["ranges"]:
        if rule["min"] <= final_score <= rule["max"]:
            matched = rule
            break

    if matched is None:
        matched = scoring_rules["ranges"][-1]

    return final_score, raw_total, matched


def _build_suggestions(scale_type: str, level: str, answers: list[int]) -> list[str]:
    """根据量表类型、风险等级和答案生成建议。"""
    suggestions: list[str] = []

    # PHQ-9 第 9 题为自杀意念，任何非 0 答案都触发危机提示
    if scale_type == "phq9" and len(answers) >= 9 and answers[8] > 0:
        suggestions.extend(CRISIS_SUGGESTIONS)
        return suggestions

    if level in GENERAL_SUGGESTIONS:
        suggestions.extend(GENERAL_SUGGESTIONS[level])
    else:
        suggestions.extend(GENERAL_SUGGESTIONS["mild"])

    return suggestions[:3]


# ─── 路由 ──────────────────────────────────────────────────────────────────────

@router.get("/scales", response_model=list[ScaleBrief], summary="获取量表列表")
async def get_scales():
    """返回所有可用量表的简要信息。"""
    return list_scales()


@router.get("/scales/{scale_type}", response_model=ScaleDetail, summary="获取量表详情")
async def get_scale_detail(scale_type: str):
    """返回指定量表的完整题目与选项。"""
    scale = get_scale(scale_type)
    if scale is None:
        raise HTTPException(status_code=404, detail=f"量表 {scale_type} 不存在")
    return ScaleDetail(
        scale_type=scale_type.lower(),
        name=scale["name"],
        title=scale["title"],
        description=scale["description"],
        category=scale["category"],
        questions=[ScaleQuestion(id=q["id"], text=q["text"]) for q in scale["questions"]],
        options=[ScaleOption(label=o["label"], value=o["value"]) for o in scale["options"]],
        reverse_items=scale.get("reverse_items", []),
    )


@router.post(
    "/submit",
    response_model=AssessmentResult,
    status_code=status.HTTP_201_CREATED,
    summary="提交量表答案并评分",
)
async def submit_assessment(
    body: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交答案，自动计算分数、生成解读并保存记录。"""
    scale = get_scale(body.scale_type)
    if scale is None:
        raise HTTPException(status_code=400, detail=f"不支持的量表类型: {body.scale_type}")

    final_score, raw_score, rule = _calculate_score(body.scale_type, body.answers)
    suggestions = _build_suggestions(body.scale_type, rule["level"], body.answers)

    assessment = Assessment(
        user_id=current_user.id,
        scale_type=body.scale_type.lower(),
        answers=json.dumps(body.answers, ensure_ascii=False),
        total_score=final_score,
        interpretation=rule["label"],
    )
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)

    logger.info(
        "用户 %s 完成 %s 测评，得分 %s，解读 %s",
        current_user.id,
        body.scale_type,
        final_score,
        rule["label"],
    )

    return AssessmentResult(
        score=final_score,
        raw_score=raw_score,
        interpretation=rule["label"],
        level=rule["level"],
        suggestions=suggestions,
        scale_type=body.scale_type.lower(),
        created_at=assessment.created_at.isoformat(),
    )


@router.get("/history", response_model=AssessmentHistoryResponse, summary="获取测评历史")
async def get_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页获取当前用户的测评历史记录。"""
    total_result = await db.execute(
        select(Assessment).where(Assessment.user_id == current_user.id)
    )
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(Assessment)
        .where(Assessment.user_id == current_user.id)
        .order_by(desc(Assessment.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    assessments = result.scalars().all()

    items: list[AssessmentHistoryItem] = []
    for a in assessments:
        scale_conf = get_scale(a.scale_type)
        scale_name = scale_conf["name"] if scale_conf else a.scale_type.upper()
        items.append(
            AssessmentHistoryItem(
                id=a.id,
                scale_type=a.scale_type,
                scale_name=scale_name,
                total_score=a.total_score,
                interpretation=a.interpretation,
                created_at=a.created_at.isoformat(),
            )
        )

    return AssessmentHistoryResponse(total=total, items=items, page=page, page_size=page_size)


@router.get("/history/{assessment_id}", response_model=AssessmentDetailResponse, summary="获取单次测评详情")
async def get_history_detail(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取某次测评的完整详情。"""
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == current_user.id,
        )
    )
    assessment = result.scalar_one_or_none()
    if assessment is None:
        raise HTTPException(status_code=404, detail="未找到该测评记录")

    scale = get_scale(assessment.scale_type)
    scale_name = scale["name"] if scale else assessment.scale_type.upper()

    return AssessmentDetailResponse(
        id=assessment.id,
        scale_type=assessment.scale_type,
        scale_name=scale_name,
        answers=json.loads(assessment.answers),
        total_score=assessment.total_score,
        interpretation=assessment.interpretation,
        created_at=assessment.created_at.isoformat(),
    )
