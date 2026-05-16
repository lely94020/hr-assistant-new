from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.interview_evaluation_service import generate_interview_evaluation
from app.crud.interview_evaluation import (
    get_evaluations_by_resume_id,
    get_latest_evaluation_by_resume_id,
    get_evaluation_by_id,
    update_hr_comment
)
from app.crud.resume import get_resume
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