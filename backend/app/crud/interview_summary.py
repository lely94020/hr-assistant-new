from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.interview_summary import InterviewSummary
from typing import List, Optional


def get_interview_summaries(db: Session, skip: int = 0, limit: int = 100,
                           resume_id: Optional[int] = None) -> List[InterviewSummary]:
    """获取面试摘要列表"""
    query = db.query(InterviewSummary)

    if resume_id is not None:
        query = query.filter(InterviewSummary.resume_id == resume_id)

    return query.order_by(desc(InterviewSummary.created_at)).offset(skip).limit(limit).all()


def get_summary_by_recording_id(db: Session, recording_id: int) -> Optional[InterviewSummary]:
    """根据录音ID获取面试摘要"""
    return db.query(InterviewSummary).filter(
        InterviewSummary.recording_id == recording_id
    ).first()


def get_summary_by_id(db: Session, summary_id: int) -> Optional[InterviewSummary]:
    """根据ID获取面试摘要"""
    return db.query(InterviewSummary).filter(
        InterviewSummary.id == summary_id
    ).first()


def create_interview_summary(
    db: Session,
    recording_id: int,
    resume_id: int,
    summary_overview: str,
    key_qa: Optional[list] = None,
    technical_skills: Optional[list] = None,
    soft_skills: Optional[list] = None,
    highlights: Optional[str] = None,
    concerns: Optional[str] = None,
    candidate_questions: Optional[str] = None
) -> InterviewSummary:
    """创建面试摘要"""
    # 将列表转换为字符串（如果传入的是列表）
    if isinstance(highlights, list):
        highlights = '\n'.join(highlights) if highlights else None
    if isinstance(concerns, list):
        concerns = '\n'.join(concerns) if concerns else None
    if isinstance(candidate_questions, list):
        candidate_questions = '\n'.join(candidate_questions) if candidate_questions else None
    
    db_summary = InterviewSummary(
        recording_id=recording_id,
        resume_id=resume_id,
        summary_overview=summary_overview,
        key_qa=key_qa,
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        highlights=highlights,
        concerns=concerns,
        candidate_questions=candidate_questions
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


def update_interview_summary(
    db: Session,
    summary_id: int,
    summary_overview: Optional[str] = None,
    key_qa: Optional[list] = None,
    technical_skills: Optional[list] = None,
    soft_skills: Optional[list] = None,
    highlights: Optional[str] = None,
    concerns: Optional[str] = None,
    candidate_questions: Optional[str] = None
) -> Optional[InterviewSummary]:
    """更新面试摘要"""
    db_summary = db.query(InterviewSummary).filter(
        InterviewSummary.id == summary_id
    ).first()

    if db_summary:
        if summary_overview is not None:
            db_summary.summary_overview = summary_overview
        if key_qa is not None:
            db_summary.key_qa = key_qa
        if technical_skills is not None:
            db_summary.technical_skills = technical_skills
        if soft_skills is not None:
            db_summary.soft_skills = soft_skills
        # 将列表转换为字符串
        if highlights is not None:
            db_summary.highlights = '\n'.join(highlights) if isinstance(highlights, list) else highlights
        if concerns is not None:
            db_summary.concerns = '\n'.join(concerns) if isinstance(concerns, list) else concerns
        if candidate_questions is not None:
            db_summary.candidate_questions = '\n'.join(candidate_questions) if isinstance(candidate_questions, list) else candidate_questions
        
        db.commit()
        db.refresh(db_summary)

    return db_summary


def delete_interview_summary(db: Session, summary_id: int) -> bool:
    """删除面试摘要"""
    db_summary = db.query(InterviewSummary).filter(
        InterviewSummary.id == summary_id
    ).first()

    if db_summary:
        db.delete(db_summary)
        db.commit()
        return True

    return False