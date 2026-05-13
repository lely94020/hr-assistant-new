from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 简历上传响应
class ResumeUploadResult(BaseModel):
    file_name: str
    status: str
    resume_id: Optional[int] = None
    error: Optional[str] = None


class ResumeUploadResponse(BaseModel):
    total: int
    success: int
    failed: int
    results: List[ResumeUploadResult]


# 简历创建请求
class ResumeCreate(BaseModel):
    candidate_name: str = Field(..., max_length=50, description="候选人姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    education: Optional[str] = Field(None, max_length=20, description="学历")
    school: Optional[str] = Field(None, max_length=100, description="毕业院校")
    major: Optional[str] = Field(None, max_length=100, description="专业")
    work_years: Optional[int] = Field(None, description="工作年限")
    current_company: Optional[str] = Field(None, max_length=100, description="当前公司")
    current_position: Optional[str] = Field(None, max_length=100, description="当前职位")
    skills: Optional[List[str]] = Field(None, description="技能标签数组")
    work_experience: Optional[List[dict]] = Field(None, description="工作经历")
    project_experience: Optional[List[dict]] = Field(None, description="项目经验")
    education_experience: Optional[List[dict]] = Field(None, description="教育经历")
    resume_summary: Optional[str] = Field(None, description="AI生成的简历摘要")
    original_content: Optional[str] = Field(None, description="简历原始文本内容")
    file_path: str = Field(..., max_length=500, description="原始文件存储路径")
    file_name: str = Field(..., max_length=200, description="原始文件名")
    file_type: str = Field(..., max_length=10, description="文件类型：pdf/docx/doc")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    position_id: Optional[int] = Field(None, description="关联岗位ID")


# 简历更新请求
class ResumeUpdate(BaseModel):
    candidate_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    education: Optional[str] = Field(None, max_length=20)
    school: Optional[str] = Field(None, max_length=100)
    major: Optional[str] = Field(None, max_length=100)
    work_years: Optional[int] = Field(None)
    current_company: Optional[str] = Field(None, max_length=100)
    current_position: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = None
    work_experience: Optional[List[dict]] = None
    project_experience: Optional[List[dict]] = None
    education_experience: Optional[List[dict]] = None
    resume_summary: Optional[str] = None
    position_id: Optional[int] = None


# 简历详情响应
class ResumeDetailResponse(BaseModel):
    id: int
    candidate_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    education: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    work_years: Optional[int] = None
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    skills: Optional[List[str]] = None
    work_experience: Optional[List[dict]] = None
    project_experience: Optional[List[dict]] = None
    education_experience: Optional[List[dict]] = None
    resume_summary: Optional[str] = None
    file_path: str
    file_name: str
    file_type: str
    file_size: Optional[int] = None
    position_id: Optional[int] = None
    status: int
    status_name: str = ""
    parse_status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # 状态名称映射
        status_map = {
            1: "待筛选",
            2: "初筛通过",
            3: "面试中",
            4: "已录用",
            5: "已淘汰"
        }
        self.status_name = status_map.get(self.status, "未知")


# 简历列表项响应
class ResumeListItem(BaseModel):
    id: int
    candidate_name: str
    phone: Optional[str] = None
    education: Optional[str] = None
    work_years: Optional[int] = None
    current_company: Optional[str] = None
    position_id: Optional[int] = None
    status: int
    status_name: str = ""
    created_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # 状态名称映射
        status_map = {
            1: "待筛选",
            2: "初筛通过",
            3: "面试中",
            4: "已录用",
            5: "已淘汰"
        }
        self.status_name = status_map.get(self.status, "未知")


# 简历列表响应
class ResumeListResponse(BaseModel):
    total: int
    items: List[ResumeListItem]
    page: int
    page_size: int


# 关联岗位请求
class BindPositionRequest(BaseModel):
    position_id: int


# 更新状态请求
class UpdateStatusRequest(BaseModel):
    status: int


# 批量下载请求
class BatchDownloadRequest(BaseModel):
    resume_ids: List[int]


# 批量删除请求
class BatchDeleteRequest(BaseModel):
    resume_ids: List[int]
