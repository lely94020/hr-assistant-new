"""
直接测试DashScope API响应结构
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.utils.oss_uploader import oss_uploader
import dashscope
from dashscope.audio.asr import Transcription


def test_dashscope_response():
    """测试DashScope API的响应结构"""
    print("=" * 60)
    print("测试DashScope API响应结构")
    print("=" * 60)

    # 配置API Key
    dashscope.api_key = settings.DASHSCOPE_API_KEY
    print(f"\nAPI Key: {settings.DASHSCOPE_API_KEY[:20]}...")

    # 查找录音文件
    recordings_dir = "uploads/recordings"
    audio_files = []
    for file in os.listdir(recordings_dir):
        if file.endswith(('.mp3', '.wav', '.m4a', '.aac')):
            audio_files.append(os.path.join(recordings_dir, file))

    if not audio_files:
        print("❌ 没有找到音频文件")
        return

    audio_file = audio_files[0]
    print(f"\n测试文件: {audio_file}")

    # 上传到OSS
    filename = os.path.basename(audio_file)
    object_name = oss_uploader.generate_object_name(filename)
    oss_url = oss_uploader.upload_file(audio_file, object_name)
    print(f"OSS URL: {oss_url}")

    try:
        print("\n调用 Transcription.async_call...")
        task = Transcription.async_call(
            model='paraformer-v2',
            file_urls=[oss_url],
            language_hints=['zh', 'en']
        )

        print(f"\nTask 类型: {type(task)}")
        print(f"Task 属性: {dir(task)}")
        print(f"\nTask 内容:")
        print(task)

        if hasattr(task, 'output'):
            print(f"\ntask.output: {task.output}")
            if task.output:
                print(f"task.output 类型: {type(task.output)}")
                print(f"task.output 属性: {dir(task.output)}")

                if hasattr(task.output, 'task_id'):
                    task_id = task.output.task_id
                    print(f"\ntask_id: {task_id}")

                    # 等待结果
                    print("\n等待转写完成...")
                    response = Transcription.wait(task_id)

                    print(f"\nResponse 类型: {type(response)}")
                    print(f"Response 属性: {dir(response)}")
                    print(f"\nResponse 内容:")
                    print(response)

                    if hasattr(response, 'output'):
                        print(f"\nresponse.output: {response.output}")
                        if response.output:
                            print(f"response.output 类型: {type(response.output)}")
                            print(f"response.output 属性: {dir(response.output)}")

                            if hasattr(response.output, 'results'):
                                print(f"\nresponse.output.results: {response.output.results}")
                                if response.output.results:
                                    print(f"results 类型: {type(response.output.results)}")
                                    print(f"results 长度: {len(response.output.results)}")

                                    for i, result in enumerate(response.output.results):
                                        print(f"\nresult[{i}]: {result}")
                                        print(f"result[{i}] 类型: {type(result)}")
                                        print(f"result[{i}] 属性: {dir(result)}")

                                        if hasattr(result, 'transcription_text'):
                                            text = result.transcription_text
                                            print(f"transcription_text 长度: {len(text)}")
                                            print(f"前100字符: {text[:100]}")

                    # 尝试以字典方式访问
                    print("\n\n尝试将response转换为字典...")
                    if hasattr(response, '__dict__'):
                        print(f"response.__dict__: {response.__dict__}")

        else:
            print("task 没有 output 属性")

        # 清理
        print("\n删除OSS文件...")
        oss_uploader.delete_file(object_name)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

        # 清理
        try:
            oss_uploader.delete_file(object_name)
        except:
            pass


if __name__ == "__main__":
    test_dashscope_response()