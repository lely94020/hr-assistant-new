from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.interview_evaluation import InterviewEvaluation
from typing import List, Optional


def get_evaluations_by_resume_id(db: Session, resume_id: int, skip: int = 0, limit: int = 100) -> List[InterviewEvaluation]:
    """根据简历ID获取评价列表"""
    return db.query(InterviewEvaluation).filter(
        InterviewEvaluation.resume_id == resume_id
    ).order_by(desc(InterviewEvaluation.created_at)).offset(skip).limit(limit).all()


def get_latest_evaluation_by_resume_id(db: Session, resume_id: int) -> Optional[InterviewEvaluation]:
    """获取简历的最新评价"""
    return db.query(InterviewEvaluation).filter(
        InterviewEvaluation.resume_id == resume_id
    ).order_by(desc(InterviewEvaluation.created_at)).first()


def get_evaluation_by_id(db: Session, evaluation_id: int) -> Optional[InterviewEvaluation]:
    """根据ID获取评价"""
    return db.query(InterviewEvaluation).filter(
        InterviewEvaluation.id == evaluation_id
    ).first()


def create_interview_evaluation(
    db: Session,
    resume_id: int,
    recording_id: Optional[int],
    summary_id: Optional[int],
    professional_score: int,
    professional_comment: Optional[str],
    logic_score: int,
    logic_comment: Optional[str],
    communication_score: int,
    communication_comment: Optional[str],
    learning_score: int,
    learning_comment: Optional[str],
    teamwork_score: int,
    teamwork_comment: Optional[str],
    culture_score: int,
    culture_comment: Optional[str],
    total_score: float,
    recommendation: str,
    ai_comment: Optional[str] = None,
    key_strengths: Optional[List[str]] = None,
    improvement_areas: Optional[List[str]] = None,
    hiring_suggestion: Optional[str] = None,
    hr_comment: Optional[str] = None
) -> InterviewEvaluation:
    """创建面试评价"""
    db_evaluation = InterviewEvaluation(
        resume_id=resume_id,
        recording_id=recording_id,
        summary_id=summary_id,
        professional_score=professional_score,
        professional_comment=professional_comment,
        logic_score=logic_score,
        logic_comment=logic_comment,
        communication_score=communication_score,
        communication_comment=communication_comment,
        learning_score=learning_score,
        learning_comment=learning_comment,
        teamwork_score=teamwork_score,
        teamwork_comment=teamwork_comment,
        culture_score=culture_score,
        culture_comment=culture_comment,
        total_score=total_score,
        recommendation=recommendation,
        ai_comment=ai_comment,
        key_strengths=key_strengths,
        improvement_areas=improvement_areas,
        hiring_suggestion=hiring_suggestion,
        hr_comment=hr_comment
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def update_interview_evaluation(
    db: Session,
    evaluation_id: int,
    professional_score: int,
    professional_comment: Optional[str],
    logic_score: int,
    logic_comment: Optional[str],
    communication_score: int,
    communication_comment: Optional[str],
    learning_score: int,
    learning_comment: Optional[str],
    teamwork_score: int,
    teamwork_comment: Optional[str],
    culture_score: int,
    culture_comment: Optional[str],
    total_score: float,
    recommendation: str,
    ai_comment: Optional[str] = None,
    key_strengths: Optional[List[str]] = None,
    improvement_areas: Optional[List[str]] = None,
    hiring_suggestion: Optional[str] = None
) -> Optional[InterviewEvaluation]:
    """更新面试评价（用于重新生成时）"""
    db_evaluation = db.query(InterviewEvaluation).filter(
        InterviewEvaluation.id == evaluation_id
    ).first()

    if db_evaluation:
        db_evaluation.professional_score = professional_score
        db_evaluation.professional_comment = professional_comment
        db_evaluation.logic_score = logic_score
        db_evaluation.logic_comment = logic_comment
        db_evaluation.communication_score = communication_score
        db_evaluation.communication_comment = communication_comment
        db_evaluation.learning_score = learning_score
        db_evaluation.learning_comment = learning_comment
        db_evaluation.teamwork_score = teamwork_score
        db_evaluation.teamwork_comment = teamwork_comment
        db_evaluation.culture_score = culture_score
        db_evaluation.culture_comment = culture_comment
        db_evaluation.total_score = total_score
        db_evaluation.recommendation = recommendation
        db_evaluation.ai_comment = ai_comment
        db_evaluation.key_strengths = key_strengths
        db_evaluation.improvement_areas = improvement_areas
        db_evaluation.hiring_suggestion = hiring_suggestion
        
        db.commit()
        db.refresh(db_evaluation)

    return db_evaluation


def update_hr_comment(db: Session, evaluation_id: int, hr_comment: str) -> Optional[InterviewEvaluation]:
    """更新HR补充评价"""
    db_evaluation = db.query(InterviewEvaluation).filter(
        InterviewEvaluation.id == evaluation_id
    ).first()

    if db_evaluation:
        db_evaluation.hr_comment = hr_comment
        db.commit()
        db.refresh(db_evaluation)

    return db_evaluation


def delete_interview_evaluation(db: Session, evaluation_id: int) -> bool:
    """删除面试评价"""
    db_evaluation = db.query(InterviewEvaluation).filter(
        InterviewEvaluation.id == evaluation_id
    ).first()

    if db_evaluation:
        db.delete(db_evaluation)
        db.commit()
        return True

    return False