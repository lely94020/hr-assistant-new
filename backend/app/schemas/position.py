from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 这段代码叫 Pydantic 模型（数据验证 + 接口格式定义）
# 作用：规定前端传什么、后端返回什么，相当于接口的“合同”。

# 创建岗位请求
class PositionCreate(BaseModel):
    position_name: str = Field(..., max_length=100, description="岗位名称")
    department: str = Field(..., max_length=100, description="所属部门")
    job_description: str = Field(..., description="岗位职责")
    requirements: str = Field(..., description="任职要求")
    salary_range: Optional[str] = Field(None, max_length=50, description="薪资范围")
    work_location: Optional[str] = Field(None, max_length=100, description="工作地点")
    headcount: int = Field(default=1, ge=1, description="招聘人数")
    status: int = Field(default=1, ge=1, le=3, description="状态")

# 更新岗位请求
class PositionUpdate(BaseModel):
    position_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    job_description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    work_location: Optional[str] = None
    headcount: Optional[int] = Field(None, ge=1)
    status: Optional[int] = Field(None, ge=1, le=3)

# 岗位响应
class PositionResponse(BaseModel):
    id: int
    position_name: str
    department: str
    job_description: str
    requirements: str
    salary_range: Optional[str]
    work_location: Optional[str]
    headcount: int
    status: int
    status_name: str = ""
    created_at: datetime
    updated_at: datetime

    # 可以把数据库查出来的对象 → 直接转成JSON返回
    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # 状态名称映射
        status_map = {1: "开放招聘", 2: "暂停招聘", 3: "已关闭"}
        self.status_name = status_map.get(self.status, "未知")

# 分页响应
class PositionListResponse(BaseModel):
    total: int
    items: list[PositionResponse]
    page: int
    page_size: int