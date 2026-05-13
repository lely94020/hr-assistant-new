from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.db.database import get_db
from app.models.user import SysUser, UserToken
from app.schemas.users import User, LoginResponse, LogoutResponse, TokenVerifyResponse, UserResponse

router = APIRouter(prefix="/api/v1/login", tags=["登录"])

SECRET_KEY = "Hr@ssistant2026!Secure#Key$9x7mP2qL5nR8wT3vB6jF0dG4hJ1kM"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """验证用户身份"""
    # 从数据库查询用户
    user = db.query(SysUser).filter(SysUser.username == username).first()
    
    if not user:
        return None
    
    # 检查用户状态
    if user.status != 1:
        return None
    
    # 验证密码
    if not verify_password(password, user.password):
        return None
    
    return user


@router.post("", response_model=LoginResponse, summary="用户登录")
def login(user_data: User, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT token和用户信息
    """
    # 验证用户
    user = authenticate_user(db, user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # 计算过期时间
    expires_at = datetime.utcnow() + access_token_expires
    
    # 保存token到数据库
    token_record = UserToken(
        user_id=user.id,
        token=access_token,
        expires_at=expires_at
    )
    db.add(token_record)
    
    # 更新用户最后登录时间
    user.last_login_time = datetime.utcnow()
    db.commit()
    db.refresh(token_record)
    db.refresh(user)
    
    # 构建用户响应
    user_response = UserResponse(
        user_id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar
    )
    
    return LoginResponse(
        message="登录成功",
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/logout", response_model=LogoutResponse, summary="用户登出")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    用户登出接口
    
    使当前token失效
    """
    # 从数据库中删除token
    token_record = db.query(UserToken).filter(UserToken.token == token).first()
    
    if token_record:
        db.delete(token_record)
        db.commit()
    
    return LogoutResponse(message="登出成功")


@router.get("/verify", response_model=TokenVerifyResponse, summary="验证token")
def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    验证token有效性
    
    返回当前用户信息
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查token是否在数据库中有效
        token_record = db.query(UserToken).filter(
            UserToken.token == token,
            UserToken.user_id == user_id
        ).first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token已失效",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查是否过期
        if datetime.utcnow() > token_record.expires_at:
            db.delete(token_record)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查询用户信息
        user = db.query(SysUser).filter(SysUser.id == user_id).first()
        
        if not user or user.status != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_response = UserResponse(
            user_id=user.id,
            username=user.username,
            real_name=user.real_name,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar
        )
        
        return TokenVerifyResponse(
            valid=True,
            user=user_response
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token",
            headers={"WWW-Authenticate": "Bearer"},
        )
