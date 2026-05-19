from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.services.interview_evaluation_service import generate_interview_evaluation
from app.crud.interview_evaluation import (
    get_evaluations_by_resume_id,
    get_latest_evaluation_by_resume_id,
    get_evaluation_by_id,
    update_hr_comment,
    delete_interview_evaluation
)
from app.crud.resume import get_resume
from app.models.interview_evaluation import InterviewEvaluation
from app.models.resume import Resume
from app.schemas.interview_evaluation import (
    GenerateEvaluationRequest,
    InterviewEvaluationResponse,
    HRCommentRequest
)

router = APIRouter(prefix="/api/v1/evaluations", tags=["面试评价"])


def format_evaluation_response(evaluation) -> dict:
    """格式化评价响应数据"""
    return {
        "id": evaluation.id,
        "resume_id": evaluation.resume_id,
        "recording_id": evaluation.recording_id,
        "summary_id": evaluation.summary_id,
        "scores": {
            "professional": {
                "score": evaluation.professional_score,
                "comment": evaluation.professional_comment
            },
            "logic": {
                "score": evaluation.logic_score,
                "comment": evaluation.logic_comment
            },
            "communication": {
                "score": evaluation.communication_score,
                "comment": evaluation.communication_comment
            },
            "learning": {
                "score": evaluation.learning_score,
                "comment": evaluation.learning_comment
            },
            "teamwork": {
                "score": evaluation.teamwork_score,
                "comment": evaluation.teamwork_comment
            },
            "culture_fit": {
                "score": evaluation.culture_score,
                "comment": evaluation.culture_comment
            }
        },
        "total_score": float(evaluation.total_score),
        "recommendation": evaluation.recommendation,
        "ai_comment": evaluation.ai_comment,
        "key_strengths": evaluation.key_strengths or [],
        "improvement_areas": evaluation.improvement_areas or [],
        "hiring_suggestion": evaluation.hiring_suggestion,
        "hr_comment": evaluation.hr_comment,
        "created_at": evaluation.created_at,
        "updated_at": evaluation.updated_at
    }


def get_level_from_score(score: float) -> str:
    """根据分数获取推荐等级"""
    if score >= 90:
        return "强烈推荐"
    elif score >= 75:
        return "推荐"
    elif score >= 60:
        return "可考虑"
    else:
        return "不推荐"


@router.get("", summary="获取面试评价列表")
def get_evaluation_list(
    keyword: Optional[str] = Query(None, description="候选人姓名搜索"),
    position: Optional[str] = Query(None, description="岗位筛选"),
    level: Optional[str] = Query(None, description="等级筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db)
):
    """获取面试评价列表（支持搜索和筛选）"""
    try:
        # 构建查询
        query = db.query(InterviewEvaluation).join(
            Resume, InterviewEvaluation.resume_id == Resume.id
        ).filter(
            Resume.is_deleted == 0
        )
        
        # 姓名搜索
        if keyword:
            query = query.filter(Resume.candidate_name.like(f"%{keyword}%"))
        
        # 岗位筛选
        if position:
            query = query.filter(Resume.current_position.like(f"%{position}%"))
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        evaluations = query.order_by(
            InterviewEvaluation.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化数据
        items = []
        for evaluation in evaluations:
            resume = get_resume(db, evaluation.resume_id)
            if resume:
                level = get_level_from_score(float(evaluation.total_score))
                
                # 如果指定了等级筛选，检查是否匹配
                if level and level != level:
                    continue
                
                items.append({
                    "id": evaluation.id,
                    "candidate_name": resume.candidate_name,
                    "position": resume.current_position or "未知岗位",
                    "total_score": float(evaluation.total_score),
                    "level": level,
                    "ai_comment": evaluation.ai_comment[:100] + "..." if evaluation.ai_comment and len(evaluation.ai_comment) > 100 else evaluation.ai_comment,
                    "created_at": evaluation.created_at,
                    "avatar": None  # 可以后续添加头像字段
                })
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": total,
                "items": items,
                "page": page,
                "page_size": page_size
            }
        }
        
    except Exception as e:
        print(f"获取评价列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取评价列表失败: {str(e)}")


@router.get("/detail/{evaluation_id}", summary="获取评价详情")
def get_evaluation_detail(evaluation_id: int, db: Session = Depends(get_db)):
    """获取面试评价详情（包含候选人信息）"""
    try:
        # 获取评价
        evaluation = get_evaluation_by_id(db, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail=f"评价不存在: evaluation_id={evaluation_id}")
        
        # 获取简历信息
        resume = get_resume(db, evaluation.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail=f"简历不存在: resume_id={evaluation.resume_id}")
        
        # 格式化响应
        response_data = format_evaluation_response(evaluation)
        
        # 添加候选人信息
        response_data["candidate_info"] = {
            "name": resume.candidate_name,
            "position": resume.current_position or "未知岗位",
            "education": resume.education,
            "work_years": resume.work_years,
            "phone": resume.phone,
            "email": resume.email
        }
        
        # 添加推荐等级
        response_data["level"] = get_level_from_score(float(evaluation.total_score))
        
        return {
            "code": 0,
            "message": "success",
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取评价详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取评价详情失败: {str(e)}")


@router.post("/generate", response_model=InterviewEvaluationResponse, summary="生成面试评价")
async def generate_evaluation(
    request: GenerateEvaluationRequest,
    db: Session = Depends(get_db)
):
    """基于面试摘要AI生成面试评价"""
    try:
        evaluation_data = generate_interview_evaluation(request.summary_id, db)
        return InterviewEvaluationResponse(**evaluation_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成评价失败: {str(e)}")


@router.get("/{resume_id}", response_model=dict, summary="获取最新评价")
def get_latest_evaluation(resume_id: int, db: Session = Depends(get_db)):
    """获取候选人的最新面试评价（包含候选人信息）"""
    try:
        # 获取简历信息
        resume = get_resume(db, resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail=f"简历不存在: resume_id={resume_id}")

        # 获取评价
        evaluation = get_latest_evaluation_by_resume_id(db, resume_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail=f"未找到面试评价: resume_id={resume_id}")

        # 格式化响应
        response_data = format_evaluation_response(evaluation)
        
        # 添加候选人信息
        response_data["candidate_info"] = {
            "name": resume.candidate_name,
            "position": resume.current_position or "未知岗位",
            "education": resume.education,
            "work_years": resume.work_years,
            "phone": resume.phone,
            "email": resume.email
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评价失败: {str(e)}")


@router.get("/history/{resume_id}", response_model=List[InterviewEvaluationResponse], summary="获取评价历史")
def get_evaluation_history(resume_id: int, db: Session = Depends(get_db)):
    """获取候选人的所有面试评价历史"""
    try:
        evaluations = get_evaluations_by_resume_id(db, resume_id)
        
        result = []
        for evaluation in evaluations:
            result.append(InterviewEvaluationResponse(**format_evaluation_response(evaluation)))
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评价历史失败: {str(e)}")


@router.put("/{evaluation_id}/hr-comment", response_model=InterviewEvaluationResponse, summary="添加HR补充评价")
def add_hr_comment(
    evaluation_id: int,
    request: HRCommentRequest,
    db: Session = Depends(get_db)
):
    """添加或更新HR补充评价"""
    try:
        evaluation = get_evaluation_by_id(db, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail=f"面试评价不存在: evaluation_id={evaluation_id}")

        updated_evaluation = update_hr_comment(db, evaluation_id, request.hr_comment)

        if not updated_evaluation:
            raise HTTPException(status_code=500, detail="更新HR评价失败")

        # 使用格式化函数返回正确的数据结构
        return InterviewEvaluationResponse(**format_evaluation_response(updated_evaluation))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新HR评价失败: {str(e)}")


@router.delete("/{evaluation_id}", summary="删除面试评价")
def delete_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """删除指定的面试评价"""
    try:
        evaluation = get_evaluation_by_id(db, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail=f"面试评价不存在: evaluation_id={evaluation_id}")

        success = delete_interview_evaluation(db, evaluation_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除面试评价失败")

        return {
            "code": 0,
            "message": "面试评价已删除"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"删除面试评价失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除面试评价失败: {str(e)}")