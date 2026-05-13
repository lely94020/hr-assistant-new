from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class RecordingUploadResponse(BaseModel):
    """上传录音响应"""
    id: int
    file_name: str
    duration: Optional[int] = None
    duration_text: Optional[str] = None
    transcript_status: int
    transcript_status_name: str

    class Config:
        from_attributes = True


class RecordingListResponse(BaseModel):
    """录音列表项"""
    id: int
    resume_id: int
    position_id: Optional[int] = None
    file_name: str
    file_type: str
    file_size: int
    duration: Optional[int] = None
    duration_text: Optional[str] = None
    transcript_status: int
    transcript_status_name: str
    interviewer: Optional[str] = None
    interview_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecordingDetailResponse(BaseModel):
    """录音详情"""
    id: int
    resume_id: int
    position_id: Optional[int] = None
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    duration: Optional[int] = None
    transcript: Optional[str] = None
    transcript_status: int
    transcript_status_name: str
    transcript_error: Optional[str] = None
    interviewer: Optional[str] = None
    interview_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TranscribeResponse(BaseModel):
    """开始转写响应"""
    id: int
    transcript_status: int
    transcript_status_name: str
    estimated_time: Optional[str] = None

    class Config:
        from_attributes = True


class TranscriptResponse(BaseModel):
    """获取文字稿响应"""
    id: int
    transcript_status: int
    transcript: Optional[str] = None
    word_count: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateTranscriptRequest(BaseModel):
    """更新文字稿请求"""
    transcript: str


class RecordingStatusResponse(BaseModel):
    """转写状态响应"""
    id: int
    transcript_status: int
    transcript_status_name: str
    transcript_error: Optional[str] = None

    class Config:
        from_attributes = True