"""认证路由：注册 / 登录 / 获取当前用户 / 绑定家长"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import get_db
from src.models.user import User
from src.utils.auth import create_access_token, get_current_user, get_password_hash, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])


# ─── 请求体 ────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: str = Field(..., max_length=100, description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    role: str = Field("child", pattern="^(child|parent)$", description="角色：child 或 parent")


class LoginRequest(BaseModel):
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class BindParentRequest(BaseModel):
    parent_email: str = Field(..., description="家长邮箱")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    parent_id: int | None = None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


# ─── 路由 ──────────────────────────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 检查邮箱是否已存在
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 检查用户名是否已存在
    existing_name = await db.execute(select(User).where(User.username == body.username))
    if existing_name.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=get_password_hash(body.password),
        role=body.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    logger.info("新用户注册: %s (%s)", user.username, user.email)
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    logger.info("用户登录: %s", user.email)
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前认证用户信息"""
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        parent_id=current_user.parent_id,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
    )


@router.post("/bind-parent", response_model=dict)
async def bind_parent(
    body: BindParentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """孩子绑定家长"""
    if current_user.role != "child":
        raise HTTPException(status_code=400, detail="只有孩子角色可以绑定家长")

    result = await db.execute(select(User).where(User.email == body.parent_email, User.role == "parent"))
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="未找到该家长账号")

    current_user.parent_id = parent.id
    await db.flush()
    logger.info("孩子 %s 绑定家长 %s", current_user.username, parent.username)
    return {"message": "绑定成功", "parent_id": parent.id, "parent_username": parent.username}
