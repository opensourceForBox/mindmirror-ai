"""心理测评量表数据配置

包含 PHQ-9、GAD-7、PSS-10、SDS 四个经典量表的题目与评分规则。
"""
from typing import Any

# 通用 Likert 选项（0-3）
LIKERT_0_3 = [
    {"label": "几乎没有", "value": 0},
    {"label": "几天", "value": 1},
    {"label": "一半以上天数", "value": 2},
    {"label": "几乎每天", "value": 3},
]

# 通用 Likert 选项（1-4）
LIKERT_1_4 = [
    {"label": "没有或很少时间", "value": 1},
    {"label": "小部分时间", "value": 2},
    {"label": "相当多时间", "value": 3},
    {"label": "绝大部分或全部时间", "value": 4},
]

# PSS-10 专用选项（0-4）
LIKERT_0_4 = [
    {"label": "从不", "value": 0},
    {"label": "几乎不", "value": 1},
    {"label": "有时", "value": 2},
    {"label": "经常", "value": 3},
    {"label": "总是", "value": 4},
]


SCALES: dict[str, dict[str, Any]] = {
    "phq9": {
        "name": "PHQ-9",
        "title": "患者健康问卷-9",
        "description": "用于筛查和评估过去两周内抑郁症状的严重程度。",
        "category": "抑郁",
        "questions": [
            {"id": 1, "text": "做事时提不起劲或没有兴趣"},
            {"id": 2, "text": "感到心情低落、沮丧或绝望"},
            {"id": 3, "text": "入睡困难、睡不安稳或睡眠过多"},
            {"id": 4, "text": "感觉疲倦或没有活力"},
            {"id": 5, "text": "食欲不振或吃太多"},
            {"id": 6, "text": "觉得自己很糟、很失败，或让自己或家人失望"},
            {"id": 7, "text": "对事物专注有困难，例如看报纸或看电视时"},
            {"id": 8, "text": "行动或说话缓慢到别人已经察觉？或刚好相反——烦躁或坐立不安、动来动去的情况更胜于平常"},
            {"id": 9, "text": "有不如死掉或用某种方式伤害自己的念头"},
        ],
        "options": LIKERT_0_3,
        "scoring_rules": {
            "ranges": [
                {"min": 0, "max": 4, "label": "无/极轻微抑郁", "level": "none"},
                {"min": 5, "max": 9, "label": "轻度抑郁", "level": "mild"},
                {"min": 10, "max": 14, "label": "中度抑郁", "level": "moderate"},
                {"min": 15, "max": 19, "label": "中重度抑郁", "level": "moderately_severe"},
                {"min": 20, "max": 27, "label": "重度抑郁", "level": "severe"},
            ],
            "max_score": 27,
        },
        "reverse_items": [],
    },
    "gad7": {
        "name": "GAD-7",
        "title": "广泛性焦虑量表-7",
        "description": "用于评估过去两周内焦虑症状的严重程度。",
        "category": "焦虑",
        "questions": [
            {"id": 1, "text": "感到紧张、焦虑或急切"},
            {"id": 2, "text": "不能停止或控制担忧"},
            {"id": 3, "text": "对各种事情担忧过多"},
            {"id": 4, "text": "很难放松下来"},
            {"id": 5, "text": "烦躁不安，坐立不宁"},
            {"id": 6, "text": "变得容易烦恼或易怒"},
            {"id": 7, "text": "感到好像有可怕的事要发生"},
        ],
        "options": LIKERT_0_3,
        "scoring_rules": {
            "ranges": [
                {"min": 0, "max": 4, "label": "无/极轻微焦虑", "level": "none"},
                {"min": 5, "max": 9, "label": "轻度焦虑", "level": "mild"},
                {"min": 10, "max": 14, "label": "中度焦虑", "level": "moderate"},
                {"min": 15, "max": 21, "label": "重度焦虑", "level": "severe"},
            ],
            "max_score": 21,
        },
        "reverse_items": [],
    },
    "pss10": {
        "name": "PSS-10",
        "title": "知觉压力量表-10",
        "description": "用于评估过去一个月内个体感知到的压力水平。",
        "category": "压力",
        "questions": [
            {"id": 1, "text": "因发生意想不到的事情而感到心烦意乱"},
            {"id": 2, "text": "感觉无法控制自己生活中重要的事情"},
            {"id": 3, "text": "感到紧张和压力"},
            {"id": 4, "text": "成功处理生活中恼人的麻烦"},
            {"id": 5, "text": "感到自己能够应付生活中必须做的事情"},
            {"id": 6, "text": "感到事情不顺心意"},
            {"id": 7, "text": "感到自己能处理好个人问题"},
            {"id": 8, "text": "感到自己能掌控局面"},
            {"id": 9, "text": "因为无法控制的事情而生气"},
            {"id": 10, "text": "感到困难堆积如山，无法克服"},
        ],
        "options": LIKERT_0_4,
        "scoring_rules": {
            "ranges": [
                {"min": 0, "max": 13, "label": "低压力", "level": "low"},
                {"min": 14, "max": 26, "label": "中等压力", "level": "moderate"},
                {"min": 27, "max": 40, "label": "高压力", "level": "high"},
            ],
            "max_score": 40,
        },
        "reverse_items": [4, 5, 7, 8],
    },
    "sds": {
        "name": "SDS",
        "title": "抑郁自评量表",
        "description": "用于评估过去一周内抑郁状态的自评量表，结果以标准分呈现。",
        "category": "抑郁自评",
        "questions": [
            {"id": 1, "text": "我觉得闷闷不乐，情绪低沉"},
            {"id": 2, "text": "我觉得一天之中早晨最好"},
            {"id": 3, "text": "我一阵阵哭出来或觉得想哭"},
            {"id": 4, "text": "我晚上睡眠不好"},
            {"id": 5, "text": "我吃得跟平常一样多"},
            {"id": 6, "text": "我与异性密切接触时和以往一样感到愉快"},
            {"id": 7, "text": "我发觉我的体重在下降"},
            {"id": 8, "text": "我有便秘的苦恼"},
            {"id": 9, "text": "我心跳比平时快"},
            {"id": 10, "text": "我无缘无故地感到疲乏"},
            {"id": 11, "text": "我的头脑跟平常一样清楚"},
            {"id": 12, "text": "我觉得经常做的事情并没有困难"},
            {"id": 13, "text": "我觉得不安而平静不下来"},
            {"id": 14, "text": "我对将来抱有希望"},
            {"id": 15, "text": "我比平常容易生气激动"},
            {"id": 16, "text": "我觉得作出决定是容易的"},
            {"id": 17, "text": "我觉得自己是个有用的人，有人需要我"},
            {"id": 18, "text": "我的生活过得很有意思"},
            {"id": 19, "text": "我认为如果我死了，别人会生活得好些"},
            {"id": 20, "text": "平常感兴趣的事我仍然照样感兴趣"},
        ],
        "options": LIKERT_1_4,
        "scoring_rules": {
            "ranges": [
                {"min": 0, "max": 52, "label": "正常范围", "level": "normal"},
                {"min": 53, "max": 62, "label": "轻度抑郁", "level": "mild"},
                {"min": 63, "max": 72, "label": "中度抑郁", "level": "moderate"},
                {"min": 73, "max": 100, "label": "重度抑郁", "level": "severe"},
            ],
            "max_score": 100,
            "standard_score_multiplier": 1.25,
        },
        "reverse_items": [2, 5, 6, 11, 12, 14, 16, 17, 18, 20],
    },
}


def get_scale(scale_type: str) -> dict[str, Any] | None:
    """根据量表类型获取量表配置。"""
    return SCALES.get(scale_type.lower())


def list_scales() -> list[dict[str, Any]]:
    """返回所有量表简要信息列表。"""
    return [
        {
            "scale_type": key,
            "name": scale["name"],
            "title": scale["title"],
            "description": scale["description"],
            "category": scale["category"],
            "question_count": len(scale["questions"]),
            "estimated_minutes": max(1, len(scale["questions"]) // 3),
        }
        for key, scale in SCALES.items()
    ]
