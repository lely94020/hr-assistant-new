import os
import asyncio
import logging
import requests
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.recording import (
    get_recording_by_id,
    update_transcript_status,
    update_transcript
)
from app.core.config import settings
from app.utils.oss_uploader import oss_uploader

# 配置日志
logger = logging.getLogger(__name__)


async def transcribe_audio_async(recording_id: int, db: Session, file_path: str):
    """
    异步执行语音转文字（使用OSS + DashScope API）
    :param recording_id: 录音ID
    :param db: 数据库会话
    :param file_path: 本地文件路径
    :return: 转写文本
    """
    oss_url = None
    object_name = None
    
    try:
        # 更新状态为转写中
        update_transcript_status(db, recording_id, 1)
        logger.info(f"开始处理录音转写 ID={recording_id}")
        
        # 动态获取API Key
        api_key = settings.DASHSCOPE_API_KEY
        
        # 检查是否配置了API Key
        if not api_key:
            raise Exception("未配置阿里云DashScope API Key，请在.env文件中配置DASHSCOPE_API_KEY")
        
        # 导入dashscope库
        try:
            import dashscope
            from dashscope.audio.asr import Transcription
        except ImportError:
            raise Exception("未安装dashscope库，请运行: pip install dashscope")
        
        # 配置API Key
        dashscope.api_key = api_key
        
        # 构建完整的文件路径
        full_file_path = file_path if os.path.isabs(file_path) else os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(full_file_path):
            raise Exception(f"音频文件不存在: {full_file_path}")
        
        logger.info(f"音频文件路径: {full_file_path}")
        logger.info(f"文件大小: {os.path.getsize(full_file_path) / 1024 / 1024:.2f} MB")
        
        # 上传文件到OSS
        if oss_uploader.use_oss:
            logger.info("上传文件到阿里云OSS...")
            filename = os.path.basename(full_file_path)
            object_name = oss_uploader.generate_object_name(filename)
            oss_url = oss_uploader.upload_file(full_file_path, object_name)
            logger.info(f"文件已上传到OSS: {oss_url}")
        else:
            raise Exception("未配置OSS，无法进行语音识别")
        
        # 使用异步调用进行语音识别
        logger.info("开始语音识别...")
        
        # 使用 async_call 创建任务
        task = Transcription.async_call(
            model='paraformer-v2',
            file_urls=[oss_url],
            language_hints=['zh', 'en']
        )
        
        # 检查任务是否创建成功
        if hasattr(task, 'status_code') and task.status_code != 200:
            error_message = getattr(task, 'message', '未知错误')
            raise Exception(f"任务创建失败 (status={task.status_code}): {error_message}")
        
        if not hasattr(task, 'output') or not task.output:
            error_message = getattr(task, 'message', '未知错误')
            raise Exception(f"任务创建失败: {error_message}")
        
        task_id = task.output.task_id
        logger.info(f"任务创建成功，task_id={task_id}")
        
        # 等待任务完成
        logger.info("等待转写完成...")
        response = Transcription.wait(task_id)
        
        # 检查响应
        if hasattr(response, 'status_code') and response.status_code != 200:
            error_message = getattr(response, 'message', '未知错误')
            raise Exception(f"转写失败 (status={response.status_code}): {error_message}")
        
        # 提取转写文本
        transcript_text = ""
        
        if response.output and response.output.results:
            results = response.output.results
            
            # results 是一个列表，每个元素是一个字典
            for result in results:
                if isinstance(result, dict):
                    # 检查是否有 transcription_url
                    if 'transcription_url' in result:
                        transcription_url = result['transcription_url']
                        logger.info(f"从 URL 下载转写结果: {transcription_url[:100]}...")
                        
                        # 下载转写结果
                        download_response = requests.get(transcription_url)
                        if download_response.status_code == 200:
                            # 解析 JSON
                            import json
                            transcription_data = download_response.json()
                            
                            # 提取文本
                            # DashScope 返回的格式可能是不同的，需要适配
                            if 'transcripts' in transcription_data:
                                for transcript in transcription_data['transcripts']:
                                    if 'text' in transcript:
                                        transcript_text += transcript['text']
                            elif 'text' in transcription_data:
                                transcript_text = transcription_data['text']
                            else:
                                logger.warning(f"未知的转写结果格式: {list(transcription_data.keys())}")
                                transcript_text = json.dumps(transcription_data, ensure_ascii=False)
                            
                            logger.info(f"成功下载并解析转写结果，长度: {len(transcript_text)}")
                        else:
                            raise Exception(f"下载转写结果失败 (status={download_response.status_code})")
                    elif 'transcription_text' in result:
                        # 直接包含文本（旧版本API）
                        transcript_text += result['transcription_text']
                    else:
                        logger.warning(f"result 中没有找到转录文本: {result.keys()}")
                else:
                    # 对象类型
                    if hasattr(result, 'transcription_text'):
                        transcript_text += result.transcription_text
        
        # 清理空白字符
        transcript_text = transcript_text.strip()
        
        logger.info(f"最终转写文本长度: {len(transcript_text)}")
        
        if not transcript_text:
            raise Exception("转写结果为空")
        
        logger.info(f"录音转写成功 ID={recording_id}")
        logger.info(f"文本长度: {len(transcript_text)} 字符")
        
        # 更新数据库中的文字稿和状态
        update_transcript(db, recording_id, transcript_text)
        update_transcript_status(db, recording_id, 2)
        
        logger.info(f"数据库更新完成 ID={recording_id}")
        
        return transcript_text
            
    except Exception as e:
        # 更新状态为失败
        error_msg = str(e)
        logger.error(f"录音转写失败 ID={recording_id}, 错误: {error_msg}")
        import traceback
        logger.error(traceback.format_exc())
        update_transcript_status(db, recording_id, 3, error=error_msg)
        raise e
    
    finally:
        # 可选：删除OSS上的临时文件
        # if oss_url and object_name and oss_uploader.use_oss:
        #     try:
        #         oss_uploader.delete_file(object_name)
        #         logger.info(f"已删除OSS临时文件: {object_name}")
        #     except Exception as e:
        #         logger.warning(f"删除OSS文件失败: {e}")
        pass


def get_transcript_status_name(status: int) -> str:
    """获取转写状态名称"""
    status_map = {
        0: "未转写",
        1: "转写中",
        2: "已完成",
        3: "转写失败"
    }
    return status_map.get(status, "未知状态")


def format_duration(seconds: Optional[int]) -> Optional[str]:
    """格式化时长为 MM:SS 或 HH:MM:SS 格式"""
    if seconds is None:
        return None
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"