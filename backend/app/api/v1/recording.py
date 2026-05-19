import os,logging
import shutil
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.services.recording_service import (
    transcribe_audio_async,
    get_transcript_status_name,
    format_duration
)
from app.crud.recording import (
    get_recordings,
    get_recording_by_id,
    create_recording,
    update_transcript,
    delete_recording
)
from app.schemas.recording import (
    RecordingUploadResponse,
    RecordingListResponse,
    RecordingDetailResponse,
    TranscribeResponse,
    TranscriptResponse,
    UpdateTranscriptRequest,
    RecordingStatusResponse
)

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recordings", tags=["录音管理"])

# 录音文件存储目录
UPLOAD_DIR = "uploads/recordings"
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


@router.post("/upload", response_model=RecordingUploadResponse, summary="上传录音")
async def upload_recording(
    file: UploadFile = File(...),
    resume_id: int = Form(...),
    position_id: Optional[int] = Form(None),
    interview_date: Optional[str] = Form(None),
    interviewer: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """上传录音文件"""
    try:
        # 验证文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}，支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 创建上传目录
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # 流式保存文件，避免一次性加载到内存
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                
                # 检查文件大小是否超过限制
                if file_size > MAX_FILE_SIZE:
                    # 删除已写入的部分文件
                    f.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"文件大小超过限制(500MB)，当前大小: {file_size / 1024 / 1024:.2f}MB"
                    )
                
                f.write(chunk)

        # 创建数据库记录
        db_recording = create_recording(
            db=db,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_ext.lstrip('.'),
            file_size=file_size,
            resume_id=resume_id,
            position_id=position_id,
            interviewer=interviewer,
            interview_date=interview_date,
            duration=None  # 可以在后续通过音频处理库获取
        )

        return RecordingUploadResponse(
            id=db_recording.id,
            file_name=db_recording.file_name,
            duration=db_recording.duration,
            duration_text=format_duration(db_recording.duration),
            transcript_status=db_recording.transcript_status,
            transcript_status_name=get_transcript_status_name(db_recording.transcript_status)
        )

    except HTTPException:
        raise
    except Exception as e:
        # 如果发生异常，清理可能已创建的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/", response_model=list[RecordingListResponse], summary="获取录音列表")
def get_recording_list(
    skip: int = 0,
    limit: int = 100,
    resume_id: Optional[int] = None,
    transcript_status: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取录音列表"""
    try:
        recordings = get_recordings(
            db,
            skip=skip,
            limit=limit,
            resume_id=resume_id,
            transcript_status=transcript_status
        )

        result = []
        for rec in recordings:
            result.append(RecordingListResponse(
                id=rec.id,
                resume_id=rec.resume_id,
                position_id=rec.position_id,
                file_name=rec.file_name,
                file_type=rec.file_type,
                file_size=rec.file_size,
                duration=rec.duration,
                duration_text=format_duration(rec.duration),
                transcript_status=rec.transcript_status,
                transcript_status_name=get_transcript_status_name(rec.transcript_status),
                interviewer=rec.interviewer,
                interview_date=rec.interview_date,
                created_at=rec.created_at
            ))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取列表失败: {str(e)}")


@router.get("/{recording_id}", response_model=RecordingDetailResponse, summary="获取录音详情")
def get_recording_detail(recording_id: int, db: Session = Depends(get_db)):
    """获取录音详情"""
    try:
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise HTTPException(status_code=404, detail="录音不存在")

        return RecordingDetailResponse(
            id=recording.id,
            resume_id=recording.resume_id,
            position_id=recording.position_id,
            file_name=recording.file_name,
            file_path=recording.file_path,
            file_type=recording.file_type,
            file_size=recording.file_size,
            duration=recording.duration,
            transcript=recording.transcript,
            transcript_status=recording.transcript_status,
            transcript_status_name=get_transcript_status_name(recording.transcript_status),
            transcript_error=recording.transcript_error,
            interviewer=recording.interviewer,
            interview_date=recording.interview_date,
            created_at=recording.created_at,
            updated_at=recording.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}")


@router.post("/{recording_id}/transcribe", response_model=TranscribeResponse, summary="开始语音转文字")
async def start_transcription(recording_id: int, db: Session = Depends(get_db)):
    """开始语音转文字"""
    try:
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise HTTPException(status_code=404, detail="录音不存在")

        if recording.transcript_status == 1:
            raise HTTPException(status_code=400, detail="正在转写中，请勿重复提交")

        if recording.transcript_status == 2:
            raise HTTPException(status_code=400, detail="已完成转写")

        # 异步启动转写任务 - 只传递 recording_id 和 file_path，不传递 db session
        import asyncio
        from app.db.database import SessionLocal
        
        # 创建后台任务
        task = asyncio.create_task(
            transcribe_audio_async(recording_id, recording.file_path, SessionLocal)
        )
        
        # 添加异常回调，确保异常不会被静默吞掉
        task.add_done_callback(_handle_transcription_task_done)

        return TranscribeResponse(
            id=recording.id,
            transcript_status=1,
            transcript_status_name="转写中",
            estimated_time="约5分钟"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动转写失败: {str(e)}")


def _handle_transcription_task_done(task):
    """
    处理转录任务完成的回调函数
    用于捕获并记录后台任务中的异常
    """
    try:
        # 尝试获取任务结果，如果任务中有异常，这里会抛出
        result = task.result()
        logger.info(f"转录任务完成，结果长度: {len(result) if result else 0}")
    except Exception as e:
        # 记录异常，但不重新抛出（因为这是后台任务）
        logger.error(f"转录任务执行失败: {str(e)}", exc_info=True)
        # 注意：此时数据库状态应该已经在 transcribe_audio_async 的 except 块中更新为失败状态


@router.get("/{recording_id}/status", response_model=RecordingStatusResponse, summary="查询转写状态")
def get_transcription_status(recording_id: int, db: Session = Depends(get_db)):
    """查询转写状态"""
    try:
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise HTTPException(status_code=404, detail="录音不存在")

        return RecordingStatusResponse(
            id=recording.id,
            transcript_status=recording.transcript_status,
            transcript_status_name=get_transcript_status_name(recording.transcript_status),
            transcript_error=recording.transcript_error
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.get("/{recording_id}/transcript", response_model=TranscriptResponse, summary="获取文字稿")
def get_transcript(recording_id: int, db: Session = Depends(get_db)):
    """获取文字稿"""
    try:
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise HTTPException(status_code=404, detail="录音不存在")

        if recording.transcript_status != 2:
            raise HTTPException(
                status_code=400,
                detail=f"转写尚未完成，当前状态: {get_transcript_status_name(recording.transcript_status)}"
            )

        word_count = len(recording.transcript) if recording.transcript else 0

        return TranscriptResponse(
            id=recording.id,
            transcript_status=recording.transcript_status,
            transcript=recording.transcript,
            word_count=word_count,
            updated_at=recording.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文字稿失败: {str(e)}")


@router.put("/{recording_id}/transcript", response_model=TranscriptResponse, summary="手动编辑文字稿")
def update_transcript_manual(
    recording_id: int,
    request: UpdateTranscriptRequest,
    db: Session = Depends(get_db)
):
    """编辑文字稿"""
    try:
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise HTTPException(status_code=404, detail="录音不存在")

        updated_recording = update_transcript(db, recording_id, request.transcript)

        if not updated_recording:
            raise HTTPException(status_code=500, detail="更新失败")

        word_count = len(updated_recording.transcript) if updated_recording.transcript else 0

        return TranscriptResponse(
            id=updated_recording.id,
            transcript_status=updated_recording.transcript_status,
            transcript=updated_recording.transcript,
            word_count=word_count,
            updated_at=updated_recording.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文字稿失败: {str(e)}")


@router.delete("/{recording_id}", summary="删除录音")
def delete_recording_endpoint(recording_id: int, db: Session = Depends(get_db)):
    """删除录音"""
    try:
        recording = get_recording_by_id(db, recording_id)
        if not recording:
            raise HTTPException(status_code=404, detail="录音不存在")

        # 删除物理文件
        if os.path.exists(recording.file_path):
            os.remove(recording.file_path)

        # 删除数据库记录
        success = delete_recording(db, recording_id)

        if success:
            return JSONResponse(
                status_code=200,
                content={"code": 0, "message": "删除成功"}
            )
        else:
            raise HTTPException(status_code=500, detail="删除失败")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")