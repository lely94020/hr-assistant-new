# app/crud/question.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.question import InterviewQuestion


def create_questions(db: Session, questions_data: List[dict]) -> List[InterviewQuestion]:
    """批量创建面试题（优化版）"""
    if not questions_data:
        return []
    
    # 使用 add_all() 批量添加，减少 ORM 操作次数
    db_questions = [InterviewQuestion(**q_data) for q_data in questions_data]
    db.add_all(db_questions)
    
    # 一次性提交，减少数据库交互
    db.commit()
    
    # 批量刷新，获取数据库生成的 ID 等字段
    for q in db_questions:
        db.refresh(q)
    
    return db_questions


def get_questions_by_position_and_resume(
    db: Session,
    position_id: Optional[int] = None,
    resume_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[InterviewQuestion]:
    """根据岗位和简历获取面试题"""
    query = db.query(InterviewQuestion)

    if position_id:
        query = query.filter(InterviewQuestion.position_id == position_id)
    if resume_id:
        query = query.filter(InterviewQuestion.resume_id == resume_id)

    return query.offset(skip).limit(limit).all()


def get_question_by_id(db: Session, question_id: int) -> Optional[InterviewQuestion]:
    """根据ID获取单个面试题"""
    return db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()


def update_question(db: Session, question_id: int, updates: dict) -> Optional[InterviewQuestion]:
    """更新面试题"""
    db_question = get_question_by_id(db, question_id)
    if db_question:
        for key, value in updates.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question


def delete_question(db: Session, question_id: int) -> bool:
    """删除面试题"""
    db_question = get_question_by_id(db, question_id)
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False


def save_questions_to_bank(db: Session, question_ids: List[int]) -> int:
    """将题目保存到题库（设置is_saved=1）"""
    # 防御：空列表检查，避免全表更新
    if not question_ids:
        return 0
    
    updated_count = db.query(InterviewQuestion).filter(
        InterviewQuestion.id.in_(question_ids)
    ).update({InterviewQuestion.is_saved: 1}, synchronize_session='fetch')
    db.commit()
    return updated_count


def get_saved_questions(db: Session, skip: int = 0, limit: int = 100) -> List[InterviewQuestion]:
    """获取已保存到题库的题目"""
    return db.query(InterviewQuestion).filter(
        InterviewQuestion.is_saved == 1
    ).offset(skip).limit(limit).all()
