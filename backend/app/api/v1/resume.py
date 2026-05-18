from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import zipfile
from io import BytesIO

from app.db.database import get_db
from app.crud import resume as resume_crud
from app.services.resume_service import ResumeService
from app.schemas.resume import (
    ResumeUploadResponse,
    ResumeListResponse,
    ResumeDetailResponse,
    BindPositionRequest,
    UpdateStatusRequest,
    BatchDownloadRequest,
    BatchDeleteRequest,
    ResumeUpdate
)

router = APIRouter(prefix="/api/v1/resumes", tags=["简历管理"])


@router.post("/upload", response_model=ResumeUploadResponse, summary="上传简历")
async def upload_resumes(
    files: List[UploadFile] = File(..., description="简历文件列表"),
    position_id: Optional[int] = Query(None, description="关联岗位ID"),
    db: Session = Depends(get_db)
):
    """
    上传单个或多个简历文件
    支持格式：PDF, DOCX, DOC
    支持ZIP压缩包自动解压
    单次最多上传100份简历
    """
    import tempfile
    
    all_files = []
    
    # 处理每个上传的文件
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # 如果是ZIP文件，解压处理
        if file_ext == '.zip':
            try:
                # 读取ZIP文件内容
                zip_content = await file.read()
                zip_buffer = BytesIO(zip_content)
                
                # 解压ZIP
                with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                    # 检查文件数量
                    if len(zip_ref.namelist()) > 100:
                        raise HTTPException(status_code=400, detail="ZIP包内最多包含100份简历")
                    
                    # 创建临时目录
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_ref.extractall(temp_dir)
                        
                        # 遍历解压的文件
                        for extracted_filename in zip_ref.namelist():
                            extracted_path = os.path.join(temp_dir, extracted_filename)
                            
                            # 跳过目录
                            if os.path.isdir(extracted_path):
                                continue
                            
                            # 检查文件格式
                            ext = os.path.splitext(extracted_filename)[1].lower()
                            if ext in ['.pdf', '.docx', '.doc']:
                                # 创建类文件对象
                                with open(extracted_path, 'rb') as f:
                                    content = f.read()
                                    from io import BytesIO as BIO
                                    file_obj = BIO(content)
                                    file_obj.filename = os.path.basename(extracted_filename)
                                    all_files.append(file_obj)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"ZIP解压失败: {str(e)}")
        else:
            # 普通文件，直接添加
            all_files.append(file)
    
    # 限制总数量
    if len(all_files) > 100:
        raise HTTPException(status_code=400, detail="单次最多上传100份简历")
    
    # 验证文件格式
    allowed_extensions = ['.pdf', '.docx', '.doc']
    valid_files = []
    for file in all_files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext in allowed_extensions:
            valid_files.append(file)

    if not valid_files:
        raise HTTPException(status_code=400, detail="没有有效的简历文件")

    # 批量处理简历
    result = await ResumeService.process_batch_resumes(db, valid_files, position_id)

    return result


@router.get("", response_model=ResumeListResponse, summary="获取简历列表")
def get_resume_list(
    keyword: Optional[str] = Query(None, description="姓名模糊搜索"),
    position_id: Optional[int] = Query(None, description="关联岗位筛选"),
    education: Optional[str] = Query(None, description="学历筛选"),
    work_years_min: Optional[int] = Query(None, description="最小工作年限"),
    work_years_max: Optional[int] = Query(None, description="最大工作年限"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db)
):
    """分页查询简历列表"""
    # 将空字符串转换为 None
    if status == "":
        status = None
    else:
        status = int(status) if status else None
    
    result = resume_crud.get_resumes(
        db=db,
        keyword=keyword,
        position_id=position_id,
        education=education,
        work_years_min=work_years_min,
        work_years_max=work_years_max,
        status=status,
        page=page,
        page_size=page_size
    )

    return result


@router.get("/{resume_id}", response_model=ResumeDetailResponse, summary="获取简历详情")
def get_resume_detail(resume_id: int, db: Session = Depends(get_db)):
    """获取简历详细信息"""
    resume = resume_crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    return resume


@router.get("/{resume_id}/download", summary="下载简历")
def download_resume(resume_id: int, db: Session = Depends(get_db)):
    """下载原始简历文件"""
    from fastapi.responses import FileResponse

    resume = resume_crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=resume.file_path,
        filename=resume.file_name,
        media_type='application/octet-stream'
    )


@router.post("/batch-download", summary="批量下载简历")
def batch_download_resumes(request: BatchDownloadRequest, db: Session = Depends(get_db)):
    """批量下载简历（ZIP包）"""
    from fastapi.responses import StreamingResponse

    # 一次性批量查询所有简历
    resumes = resume_crud.get_resumes_by_ids(db, request.resume_ids)

    # 过滤出文件存在的简历
    valid_resumes = [r for r in resumes if os.path.exists(r.file_path)]

    if not valid_resumes:
        raise HTTPException(status_code=404, detail="没有可下载的简历")

    # 创建ZIP文件
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for resume in valid_resumes:
            zip_file.write(resume.file_path, resume.file_name)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type='application/zip',
        headers={'Content-Disposition': 'attachment; filename=resumes.zip'}
    )


@router.delete("/{resume_id}", summary="删除简历")
def delete_resume(
    resume_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """删除简历及关联数据"""
    resume = resume_crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    milvus_id = resume.milvus_id

    success = resume_crud.delete_resume(db, resume_id)
    if not success:
        raise HTTPException(status_code=404, detail="简历不存在")

    # 异步删除 Milvus 向量，不阻塞响应
    if milvus_id:
        background_tasks.add_task(ResumeService.delete_milvus_vector, milvus_id)

    return {"message": "删除成功"}


@router.post("/batch-delete", summary="批量删除简历")
def batch_delete_resumes(
    request: BatchDeleteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """批量删除多个简历"""
    if not request.resume_ids:
        raise HTTPException(status_code=400, detail="请选择要删除的简历")

    # 一次性批量查询所有简历，收集 Milvus ID
    resumes = resume_crud.get_resumes_by_ids(db, request.resume_ids)
    milvus_ids = [r.milvus_id for r in resumes if r.milvus_id]

    # 批量删除数据库记录
    count = resume_crud.batch_delete_resumes(db, request.resume_ids)

    # 异步批量删除 Milvus 向量，不阻塞响应
    if milvus_ids:
        background_tasks.add_task(ResumeService.batch_delete_milvus_vectors, milvus_ids)

    return {
        "message": f"成功删除{count}份简历",
        "deleted_count": count
    }


@router.put("/{resume_id}/bindPosition", summary="关联岗位")
def bind_position(resume_id: int, request: BindPositionRequest, db: Session = Depends(get_db)):
    """将简历关联到目标岗位"""
    resume = resume_crud.bind_position(db, resume_id, request.position_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    return {
        "code": 0,
        "message": "success",
        "data": {
            "resume_id": resume.id,
            "position_id": resume.position_id
        }
    }


@router.patch("/{resume_id}/status", summary="更新简历状态")
def update_resume_status(resume_id: int, request: UpdateStatusRequest, db: Session = Depends(get_db)):
    """更新简历流转状态"""
    # 验证状态值
    valid_statuses = [1, 2, 3, 4, 5]
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="无效的状态值")

    resume = resume_crud.update_resume_status(db, resume_id, request.status)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    return {
        "code": 0,
        "message": "success",
        "data": {
            "resume_id": resume.id,
            "status": resume.status
        }
    }


@router.put("/{resume_id}", summary="更新简历信息")
def update_resume(resume_id: int, request: ResumeUpdate, db: Session = Depends(get_db)):
    """手动修正简历解析结果"""
    resume = resume_crud.update_resume(db, resume_id, request)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "resume_id": resume.id
        }
    }


@router.post("/{resume_id}/reparse", summary="重新解析简历")
async def reparse_resume(resume_id: int, db: Session = Depends(get_db)):
    """重新解析简历内容"""
    resume = resume_crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    # 更新解析状态为解析中
    resume.parse_status = 1
    db.commit()

    try:
        # 重新解析内容
        text_content = await ResumeService.parse_resume_content(resume.file_path, resume.file_type)

        # AI提取结构化信息
        extracted_info = await ResumeService.extract_resume_info(text_content)

        # 更新简历信息
        resume.original_content = text_content
        resume.candidate_name = extracted_info.get("candidate_name", resume.candidate_name)
        resume.phone = extracted_info.get("phone")
        resume.email = extracted_info.get("email")
        resume.education = extracted_info.get("education")
        resume.school = extracted_info.get("school")
        resume.major = extracted_info.get("major")
        resume.work_years = extracted_info.get("work_years")
        resume.current_company = extracted_info.get("current_company")
        resume.current_position = extracted_info.get("current_position")
        resume.skills = extracted_info.get("skills")
        resume.work_experience = extracted_info.get("work_experience")
        resume.project_experience = extracted_info.get("project_experience")
        resume.education_experience = extracted_info.get("education_experience")
        resume.resume_summary = extracted_info.get("resume_summary")
        resume.parse_status = 2  # 解析成功

        db.commit()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "resume_id": resume.id
            }
        }

    except Exception as e:
        resume.parse_status = 3  # 解析失败
        db.commit()
        raise HTTPException(status_code=500, detail=f"解析失败：{str(e)}")
