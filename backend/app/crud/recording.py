from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.recording import InterviewRecording
from typing import List, Optional


def get_recordings(db: Session, skip: int = 0, limit: int = 100,
                   resume_id: Optional[int] = None,
                   transcript_status: Optional[int] = None) -> List[InterviewRecording]:
    """获取录音列表"""
    query = db.query(InterviewRecording)

    if resume_id is not None:
        query = query.filter(InterviewRecording.resume_id == resume_id)
    if transcript_status is not None:
        query = query.filter(InterviewRecording.transcript_status == transcript_status)

    return query.order_by(desc(InterviewRecording.created_at)).offset(skip).limit(limit).all()


def get_recording_by_id(db: Session, recording_id: int) -> Optional[InterviewRecording]:
    """根据ID获取录音"""
    return db.query(InterviewRecording).filter(InterviewRecording.id == recording_id).first()


def create_recording(db: Session, file_name: str, file_path: str, file_type: str,
                    file_size: int, resume_id: int, position_id: Optional[int] = None,
                    interviewer: Optional[str] = None, interview_date: Optional[str] = None,
                    duration: Optional[int] = None) -> InterviewRecording:
    """创建录音记录"""
    db_recording = InterviewRecording(
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        resume_id=resume_id,
        position_id=position_id,
        interviewer=interviewer,
        interview_date=interview_date,
        duration=duration,
        transcript_status=0  # 未转写
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def update_transcript_status(db: Session, recording_id: int, status: int,
                            error: Optional[str] = None) -> Optional[InterviewRecording]:
    """更新转写状态"""
    db_recording = db.query(InterviewRecording).filter(
        InterviewRecording.id == recording_id
    ).first()

    if db_recording:
        db_recording.transcript_status = status
        if error:
            db_recording.transcript_error = error
        db.commit()
        db.refresh(db_recording)

    return db_recording


def update_transcript(db: Session, recording_id: int, transcript: str) -> Optional[InterviewRecording]:
    """更新文字稿"""
    db_recording = db.query(InterviewRecording).filter(
        InterviewRecording.id == recording_id
    ).first()

    if db_recording:
        db_recording.transcript = transcript
        db_recording.transcript_status = 2  # 已完成
        db.commit()
        db.refresh(db_recording)

    return db_recording


def delete_recording(db: Session, recording_id: int) -> bool:
    """删除录音"""
    db_recording = db.query(InterviewRecording).filter(
        InterviewRecording.id == recording_id
    ).first()

    if db_recording:
        db.delete(db_recording)
        db.commit()
        return True

    return False