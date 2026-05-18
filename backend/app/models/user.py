from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from app.db.database import Base


class SysUser(Base):
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    username = Column(String(50), nullable=False, unique=True, comment='用户名')
    password = Column(String(100), nullable=False, comment='密码(加密)')
    real_name = Column(String(50), comment='真实姓名')
    email = Column(String(100), comment='邮箱')
    phone = Column(String(20), comment='手机号')
    avatar = Column(String(500), comment='头像URL')
    status = Column(Integer, nullable=False, default=1, comment='状态：1-正常 0-禁用')
    last_login_time = Column(DateTime, comment='最后登录时间')
    created_at = Column(DateTime, nullable=False, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment='更新时间')


class UserToken(Base):
    __tablename__ = "user_token"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = Column(Integer, nullable=False, index=True, comment='关联用户ID')
    token = Column(String(255), nullable=False, index=True, comment='用户登录Token')
    expires_at = Column(DateTime, nullable=False, comment='Token过期时间')
    created_at = Column(DateTime, nullable=False, default=func.now(), comment='创建时间')
