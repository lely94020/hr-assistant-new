# app/api/v1/question.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.question_service import QuestionService
from app.schemas.question import (
    QuestionGenerateRequest,
    QuestionGenerateResponse,
    QuestionUpdateRequest,
    QuestionSaveRequest,
    QuestionListResponse
)

router = APIRouter(prefix="/api/v1/questions", tags=["面试题管理"])


@router.post("/generate", response_model=QuestionGenerateResponse, summary="智能生成面试题")
async def generate_questions(
    request: QuestionGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    智能生成面试题

    - **mode**: 生成模式（position/resume/mixed）
    - **position_id**: 岗位ID（mode为position或mixed时必需）
    - **resume_id**: 简历ID（mode为resume或mixed时必需）
    - **question_types**: 题目类型列表（technical/behavioral/situational/open）
    - **difficulty**: 难度等级（junior/middle/senior）
    - **count**: 题目数量（1-20）
    - **with_answer**: 是否生成参考答案
    """
    try:
        questions = await QuestionService.generate_questions(
            db=db,
            mode=request.mode,
            position_id=request.position_id,
            resume_id=request.resume_id,
            question_types=request.question_types,
            difficulty=request.difficulty,
            count=request.count,
            with_answer=request.with_answer
        )

        return QuestionGenerateResponse(questions=questions)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("", response_model=QuestionListResponse, summary="获取面试题列表")
def get_questions(
    position_id: Optional[int] = None,
    resume_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取面试题列表

    - **position_id**: 可选，按岗位筛选
    - **resume_id**: 可选，按简历筛选
    - **page**: 页码
    - **page_size**: 每页数量
    """
    try:
        result = QuestionService.get_questions(
            db=db,
            position_id=position_id,
            resume_id=resume_id,
            page=page,
            page_size=page_size
        )
        return QuestionListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.put("/{question_id}", summary="编辑面试题")
def update_question(
    question_id: int,
    request: QuestionUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    编辑面试题

    - **question_id**: 题目ID
    - **question_content**: 题目内容
    - **reference_answer**: 参考答案
    - **scoring_points**: 评分要点
    """
    try:
        updates = request.model_dump(exclude_unset=True)
        result = QuestionService.update_question(db, question_id, updates)
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{question_id}", summary="删除面试题")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    删除面试题

    - **question_id**: 题目ID
    """
    try:
        success = QuestionService.delete_question(db, question_id)
        if not success:
            raise HTTPException(status_code=404, detail="题目不存在")

        return {
            "code": 0,
            "message": "删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/save-to-bank", summary="保存到题库")
def save_to_question_bank(
    request: QuestionSaveRequest,
    db: Session = Depends(get_db)
):
    """
    将生成的面试题保存到题库

    - **question_ids**: 要保存的题目ID列表
    """
    try:
        result = QuestionService.save_to_question_bank(db, request.question_ids)
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
