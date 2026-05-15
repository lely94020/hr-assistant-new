from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GenerateSummaryRequest(BaseModel):
    """生成摘要请求"""
    recording_id: int


class KeyQAResponse(BaseModel):
    """核心问答响应"""
    question: str
    answer_summary: str
    answer_quality: str


class InterviewSummaryResponse(BaseModel):
    """面试摘要响应"""
    id: int
    recording_id: int
    resume_id: int
    summary_overview: str
    key_qa: List[KeyQAResponse] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    highlights: Optional[str] = None
    concerns: Optional[str] = None
    candidate_questions: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateSummaryRequest(BaseModel):
    """更新摘要请求"""
    summary_overview: Optional[str] = None
    key_qa: Optional[List[Dict[str, Any]]] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    highlights: Optional[str] = None
    concerns: Optional[str] = None
    candidate_questions: Optional[str] = None