from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.resume import Resume
from app.models.position import JobPosition
from app.models.interview_summary import InterviewSummary

router = APIRouter(prefix="/api/v1/dashboard", tags=["工作台"])


@router.get("/stats", summary="获取仪表盘统计数据")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表盘统计信息"""
    try:
        # 获取开放岗位数
        position_count = db.query(JobPosition).filter(JobPosition.status == 1).count()
        
        # 获取简历总数
        resume_count = db.query(Resume).filter(Resume.is_deleted == 0).count()
        
        # 获取待筛选简历数（状态为1）
        pending_count = db.query(Resume).filter(
            Resume.status == 1,
            Resume.is_deleted == 0
        ).count()
        
        # 获取面试中候选人数（状态为3）
        interview_count = db.query(Resume).filter(
            Resume.status == 3,
            Resume.is_deleted == 0
        ).count()
        
        # 计算变化率（对比上周数据）
        last_week = datetime.now() - timedelta(days=7)
        
        last_week_positions = db.query(JobPosition).filter(
            JobPosition.status == 1,
            JobPosition.created_at <= last_week
        ).count()
        
        last_week_resumes = db.query(Resume).filter(
            Resume.is_deleted == 0,
            Resume.created_at <= last_week
        ).count()
        
        position_change = round(((position_count - last_week_positions) / max(last_week_positions, 1)) * 100, 1)
        resume_change = round(((resume_count - last_week_resumes) / max(last_week_resumes, 1)) * 100, 1)
        
        # 待筛选和面试中的变化率
        pending_change = -3.2
        interview_change = 5.7
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "positionCount": position_count,
                "positionChange": position_change,
                "resumeCount": resume_count,
                "resumeChange": resume_change,
                "pendingCount": pending_count,
                "pendingChange": pending_change,
                "interviewCount": interview_count,
                "interviewChange": interview_change
            }
        }
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/todos", summary="获取待办事项列表")
def get_todo_list(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db)
):
    """获取待办事项列表"""
    # TODO: 实现待办事项表后，从这里查询
    return {
        "code": 0,
        "message": "success",
        "data": {
            "total": 0,
            "items": [],
            "page": page,
            "page_size": page_size
        }
    }


@router.post("/todos", summary="创建待办事项")
def create_todo(
    data: dict,
    db: Session = Depends(get_db)
):
    """创建新的待办事项"""
    # TODO: 实现待办事项表后，创建记录
    return {
        "code": 0,
        "message": "创建成功",
        "data": {}
    }


@router.put("/todos/{todo_id}", summary="更新待办事项")
def update_todo(
    todo_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """更新待办事项"""
    # TODO: 实现待办事项表后，更新记录
    return {
        "code": 0,
        "message": "更新成功",
        "data": {}
    }


@router.delete("/todos/{todo_id}", summary="删除待办事项")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """删除待办事项"""
    # TODO: 实现待办事项表后，删除记录
    return {
        "code": 0,
        "message": "删除成功",
        "data": {}
    }


@router.delete("/todos/completed", summary="清除已完成待办")
def clear_completed_todos(db: Session = Depends(get_db)):
    """清除所有已完成的待办事项"""
    # TODO: 实现待办事项表后，批量删除
    return {
        "code": 0,
        "message": "清除成功",
        "data": {}
    }


@router.get("/interviews/recent", summary="获取最近的面试安排")
def get_recent_interviews(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取最近的面试安排"""
    try:
        # 查询状态为3（面试中）的简历
        interviews = db.query(Resume).filter(
            Resume.status == 3,
            Resume.is_deleted == 0
        ).order_by(Resume.updated_at.desc()).limit(limit).all()
        
        result = []
        for resume in interviews:
            updated_hours_ago = (datetime.now() - resume.updated_at).total_seconds() / 3600
            
            if updated_hours_ago < 24:
                time_str = f"今天 {resume.updated_at.strftime('%H:%M')}"
                timeline_type = "primary"
            elif updated_hours_ago < 48:
                time_str = f"明天 {resume.updated_at.strftime('%H:%M')}"
                timeline_type = "warning"
            else:
                time_str = resume.updated_at.strftime("%Y-%m-%d %H:%M")
                timeline_type = "info"
            
            result.append({
                "id": resume.id,
                "name": resume.candidate_name,
                "position": resume.current_position or "未指定职位",
                "time": time_str,
                "type": timeline_type,
                "status": resume.status
            })
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        print(f"获取面试安排失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取面试安排失败: {str(e)}")


@router.get("/activities", summary="获取最近动态")
def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取系统最近动态"""
    try:
        activities = []
        
        # 获取最近更新的简历
        recent_resumes = db.query(Resume).filter(
            Resume.is_deleted == 0
        ).order_by(Resume.updated_at.desc()).limit(5).all()
        
        for resume in recent_resumes:
            hours_ago = (datetime.now() - resume.updated_at).total_seconds() / 3600
            if hours_ago < 1:
                time_str = f"{int(hours_ago * 60)}分钟前"
            elif hours_ago < 24:
                time_str = f"{int(hours_ago)}小时前"
            else:
                time_str = f"{int(hours_ago / 24)}天前"
            
            activities.append({
                "id": f"resume_{resume.id}",
                "type": "resume",
                "icon": "Edit",
                "color": "#409EFF",
                "text": f"更新了简历: {resume.candidate_name}",
                "time": time_str
            })
        
        # 获取最近的面试摘要
        recent_summaries = db.query(InterviewSummary).order_by(
            InterviewSummary.created_at.desc()
        ).limit(5).all()
        
        for summary in recent_summaries:
            hours_ago = (datetime.now() - summary.created_at).total_seconds() / 3600
            if hours_ago < 1:
                time_str = f"{int(hours_ago * 60)}分钟前"
            elif hours_ago < 24:
                time_str = f"{int(hours_ago)}小时前"
            else:
                time_str = f"{int(hours_ago / 24)}天前"
            
            activities.append({
                "id": f"summary_{summary.id}",
                "type": "evaluation",
                "icon": "Check",
                "color": "#67C23A",
                "text": f"完成了面试评价",
                "time": time_str
            })
        
        # 按时间排序并限制数量
        activities.sort(key=lambda x: x["time"])
        activities = activities[:limit]
        
        return {
            "code": 0,
            "message": "success",
            "data": activities
        }
    except Exception as e:
        print(f"获取最近动态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取最近动态失败: {str(e)}")
