"""
测试OSS上传和DashScope流式语音识别
完整测试录音管理模块的转写功能
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.utils.oss_uploader import oss_uploader
from app.services.recording_service import transcribe_audio_async
from app.db.database import SessionLocal
from app.crud.recording import create_recording, get_recording_by_id


def test_oss_upload():
    """测试1: OSS上传功能"""
    print("=" * 60)
    print("测试1: OSS上传功能")
    print("=" * 60)

    if not oss_uploader.use_oss:
        print("❌ OSS未配置，跳过测试")
        return False

    # 查找录音文件
    recordings_dir = "../uploads/recordings"
    if not os.path.exists(recordings_dir):
        print(f"❌ 录音目录不存在: {recordings_dir}")
        return False

    audio_files = []
    for file in os.listdir(recordings_dir):
        if file.endswith(('.mp3', '.wav', '.m4a', '.aac')):
            audio_files.append(os.path.join(recordings_dir, file))

    if not audio_files:
        print(f"❌ 没有找到音频文件")
        print(f"请先通过前端上传一个录音文件到: {recordings_dir}")
        return False

    # 测试上传
    audio_file = audio_files[0]
    print(f"\n测试文件: {audio_file}")
    print(f"文件大小: {os.path.getsize(audio_file) / 1024 / 1024:.2f} MB")

    try:
        filename = os.path.basename(audio_file)
        object_name = oss_uploader.generate_object_name(filename)

        print(f"对象名称: {object_name}")

        url = oss_uploader.upload_file(audio_file, object_name)
        print(f"✅ 上传成功!")
        print(f"文件URL: {url}")

        # 验证URL是否可访问
        print("\n验证URL可访问性...")
        import requests
        response = requests.head(url)
        if response.status_code == 200:
            print("✅ URL可公开访问")
        else:
            print(f"⚠️ URL访问状态码: {response.status_code}")
            print("   请确保Bucket设置为'公共读'")

        # 测试删除
        print("\n测试删除文件...")
        success = oss_uploader.delete_file(object_name)
        if success:
            print("✅ 删除成功")
        else:
            print("⚠️ 删除失败")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streaming_transcription():
    """测试2: 流式语音识别"""
    print("\n" + "=" * 60)
    print("测试2: 流式语音识别")
    print("=" * 60)

    # 查找录音文件
    recordings_dir = "../uploads/recordings"
    if not os.path.exists(recordings_dir):
        print(f"❌ 录音目录不存在: {recordings_dir}")
        return False

    audio_files = []
    for file in os.listdir(recordings_dir):
        if file.endswith(('.mp3', '.wav', '.m4a', '.aac')):
            audio_files.append(os.path.join(recordings_dir, file))

    if not audio_files:
        print(f"❌ 没有找到音频文件")
        print(f"请先通过前端上传一个录音文件到: {recordings_dir}")
        return False

    # 使用第一个音频文件
    audio_file = audio_files[0]
    print(f"\n使用测试文件: {audio_file}")
    print(f"文件大小: {os.path.getsize(audio_file) / 1024 / 1024:.2f} MB")

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 创建一个测试录音记录
        filename = os.path.basename(audio_file)

        recording = create_recording(
            db=db,
            file_name=filename,
            file_path=audio_file,
            file_type=audio_file.split('.')[-1],
            file_size=os.path.getsize(audio_file),
            resume_id=1,  # 假设存在ID为1的简历
            position_id=None,
            interviewer="测试",
            interview_date=None,
            duration=None
        )

        print(f"✅ 创建测试录音记录 ID={recording.id}")

        # 调用流式转写
        print("\n开始流式转写...")
        print("这可能需要几分钟时间，请耐心等待...")
        import asyncio

        async def run_transcription():
            result = await transcribe_audio_async(recording.id, db, audio_file)
            return result

        # 运行异步任务
        transcript = asyncio.run(run_transcription())

        print(f"\n✅ 转写成功!")
        print(f"文本长度: {len(transcript)} 字符")
        print(f"\n前500字符:")
        print("-" * 60)
        print(transcript[:500])
        print("-" * 60)

        if len(transcript) > 500:
            print(f"\n...(还有 {len(transcript) - 500} 字符)")

        # 验证数据库更新
        updated_recording = get_recording_by_id(db, recording.id)
        print(f"\n数据库状态:")
        print(f"  转写状态: {updated_recording.transcript_status} (2表示成功)")
        print(f"  文字稿长度: {len(updated_recording.transcript) if updated_recording.transcript else 0}")

        if updated_recording.transcript_status == 2:
            print("\n✅ 数据库更新成功")
        else:
            print(f"\n⚠️ 数据库状态异常: {updated_recording.transcript_status}")
            if updated_recording.transcript_error:
                print(f"错误信息: {updated_recording.transcript_error}")

        return True

    except Exception as e:
        print(f"\n❌ 转写失败: {e}")
        import traceback
        traceback.print_exc()

        # 检查数据库中的错误信息
        try:
            updated_recording = get_recording_by_id(db, recording.id)
            if updated_recording and updated_recording.transcript_error:
                print(f"\n数据库中的错误信息:")
                print(f"  {updated_recording.transcript_error}")
        except:
            pass

        return False

    finally:
        db.close()


def print_config_info():
    """打印配置信息"""
    print("\n" + "=" * 60)
    print("当前配置信息")
    print("=" * 60)

    print(f"\nDashScope API Key: {'已配置' if settings.DASHSCOPE_API_KEY else '未配置'}")
    if settings.DASHSCOPE_API_KEY:
        print(f"  Key: {settings.DASHSCOPE_API_KEY[:20]}...")

    print(f"\nOSS配置: {'已配置' if oss_uploader.use_oss else '未配置'}")
    if oss_uploader.use_oss:
        print(f"  Bucket: {oss_uploader.bucket_name}")
        print(f"  Endpoint: {oss_uploader.endpoint}")
        print(f"  Base URL: {oss_uploader.base_url}")

    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("阿里云 OSS + DashScope 流式语音识别测试")
    print("=" * 60)

    # 打印配置信息
    print_config_info()

    # 测试1: OSS上传
    oss_success = test_oss_upload()

    # 测试2: 流式转写
    if oss_success:
        transcription_success = test_streaming_transcription()
    else:
        print("\n⚠️ OSS上传测试失败，跳过转写测试")
        transcription_success = False

    # 测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"OSS上传测试: {'✅ 通过' if oss_success else '❌ 失败'}")
    print(f"流式转写测试: {'✅ 通过' if transcription_success else '❌ 失败'}")

    if oss_success and transcription_success:
        print("\n🎉 所有测试通过！系统可以正常使用")
        print("\n下一步:")
        print("1. 启动后端服务: cd app && uvicorn main:app --reload")
        print("2. 访问前端页面进行完整功能测试")
        print("3. 查看API文档: http://localhost:8000/docs")
    elif oss_success:
        print("\n⚠️ OSS配置正确，但转写失败")
        print("请检查:")
        print("1. DashScope API Key 是否有效")
        print("2. 网络连接是否正常")
        print("3. 音频文件格式是否支持")
        print("4. 查看上方的详细错误信息")
    else:
        print("\n❌ 测试失败，请检查配置")
        print("请检查:")
        print("1. .env 文件中的 OSS 配置是否正确")
        print("2. Bucket 是否设置为'公共读'")
        print("3. AccessKey 是否有权限")

    print("=" * 60)