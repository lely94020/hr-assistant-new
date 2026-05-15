from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.interview_summary_service import generate_interview_summary
from app.crud.interview_summary import (
    get_summary_by_recording_id,
    get_summary_by_id,
    update_interview_summary,
    delete_interview_summary
)
from app.schemas.interview_summary import (
    GenerateSummaryRequest,
    InterviewSummaryResponse,
    UpdateSummaryRequest
)

router = APIRouter(prefix="/api/v1/summaries", tags=["面试摘要"])


@router.post("/generate", response_model=InterviewSummaryResponse, summary="生成面试摘要")
async def generate_summary(
    request: GenerateSummaryRequest,
    db: Session = Depends(get_db)
):
    """从录音生成面试摘要"""
    try:
        # 调用服务层生成摘要
        summary_data = generate_interview_summary(request.recording_id, db)

        return InterviewSummaryResponse(**summary_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成摘要失败: {str(e)}")


@router.get("/{recording_id}", response_model=InterviewSummaryResponse, summary="获取面试摘要")
def get_summary(recording_id: int, db: Session = Depends(get_db)):
    """获取面试摘要"""
    try:
        summary = get_summary_by_recording_id(db, recording_id)
        if not summary:
            raise HTTPException(status_code=404, detail="面试摘要不存在")

        return InterviewSummaryResponse.from_orm(summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")


@router.put("/{summary_id}", response_model=InterviewSummaryResponse, summary="更新面试摘要")
def update_summary(
    summary_id: int,
    request: UpdateSummaryRequest,
    db: Session = Depends(get_db)
):
    """编辑面试摘要"""
    try:
        # 检查摘要是否存在
        summary = get_summary_by_id(db, summary_id)
        if not summary:
            raise HTTPException(status_code=404, detail="面试摘要不存在")

        # 更新摘要
        updated_summary = update_interview_summary(
            db=db,
            summary_id=summary_id,
            summary_overview=request.summary_overview,
            key_qa=request.key_qa,
            technical_skills=request.technical_skills,
            soft_skills=request.soft_skills,
            highlights=request.highlights,
            concerns=request.concerns,
            candidate_questions=request.candidate_questions
        )

        if not updated_summary:
            raise HTTPException(status_code=500, detail="更新摘要失败")

        return InterviewSummaryResponse.from_orm(updated_summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新摘要失败: {str(e)}")


@router.post("/{summary_id}/regenerate", response_model=InterviewSummaryResponse, summary="重新生成面试摘要")
async def regenerate_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    """重新生成面试摘要"""
    try:
        # 获取现有摘要以获取录音ID
        summary = get_summary_by_id(db, summary_id)
        if not summary:
            raise HTTPException(status_code=404, detail="面试摘要不存在")

        # 重新生成摘要
        summary_data = generate_interview_summary(summary.recording_id, db)

        return InterviewSummaryResponse(**summary_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成摘要失败: {str(e)}")


@router.delete("/{summary_id}", summary="删除面试摘要")
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    """删除面试摘要"""
    try:
        summary = get_summary_by_id(db, summary_id)
        if not summary:
            raise HTTPException(status_code=404, detail="面试摘要不存在")

        success = delete_interview_summary(db, summary_id)

        if success:
            return {"code": 0, "message": "删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除摘要失败: {str(e)}")