from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应信息"""
    user_id: int
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class LoginResponse(BaseModel):
    """登录响应"""
    message: str
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class LogoutResponse(BaseModel):
    """登出响应"""
    message: str


class TokenVerifyResponse(BaseModel):
    """Token验证响应"""
    valid: bool
    user: UserResponse
