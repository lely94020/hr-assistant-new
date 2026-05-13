# app/schemas/question.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QuestionGenerateRequest(BaseModel):
    """生成面试题请求"""
    mode: str = Field(..., description="生成模式：position/resume/mixed")
    position_id: Optional[int] = Field(None, description="岗位ID")
    resume_id: Optional[int] = Field(None, description="简历ID")
    question_types: List[str] = Field(default=["technical"], description="题目类型列表")
    difficulty: str = Field(default="middle", description="难度等级")
    count: int = Field(default=5, ge=1, le=20, description="题目数量")
    with_answer: bool = Field(default=True, description="是否生成参考答案")


class QuestionItem(BaseModel):
    """单个面试题响应"""
    id: Optional[int] = None
    type: str
    type_name: str
    difficulty: str
    difficulty_name: str
    question: str
    reference_answer: Optional[str] = None
    scoring_points: Optional[List[str]] = None
    source: str


class QuestionGenerateResponse(BaseModel):
    """生成面试题响应"""
    questions: List[QuestionItem]


class QuestionUpdateRequest(BaseModel):
    """更新面试题请求"""
    question_content: Optional[str] = None
    reference_answer: Optional[str] = None
    scoring_points: Optional[List[str]] = None


class QuestionSaveRequest(BaseModel):
    """保存面试题到题库请求"""
    question_ids: List[int] = Field(..., description="要保存的题目ID列表")


class QuestionListResponse(BaseModel):
    """面试题列表响应"""
    total: int
    items: List[QuestionItem]
    page: int
    page_size: int
