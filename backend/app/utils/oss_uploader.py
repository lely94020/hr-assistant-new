"""
阿里云OSS上传工具
用于将音频文件上传到OSS，供DashScope语音识别使用
"""
import oss2
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OSSUploader:
    """阿里云OSS上传器"""

    def __init__(self):
        self.access_key_id = getattr(settings, 'OSS_ACCESS_KEY_ID', '')
        self.access_key_secret = getattr(settings, 'OSS_ACCESS_KEY_SECRET', '')
        self.bucket_name = getattr(settings, 'OSS_BUCKET_NAME', '')
        self.endpoint = getattr(settings, 'OSS_ENDPOINT', 'oss-cn-beijing.aliyuncs.com')
        self.base_url = getattr(settings, 'OSS_URL', '')

        # 检查是否配置了OSS
        if not all([self.access_key_id, self.access_key_secret, self.bucket_name]):
            self.use_oss = False
            logger.warning("未配置阿里云OSS，将使用本地文件方式（可能不被DashScope支持）")
        else:
            try:
                # 初始化认证和Bucket
                auth = oss2.Auth(self.access_key_id, self.access_key_secret)
                self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
                self.use_oss = True
                logger.info("阿里云OSS初始化成功")
            except Exception as e:
                self.use_oss = False
                logger.error(f"阿里云OSS初始化失败: {e}")

    def upload_file(self, local_file_path: str, object_name: str) -> str:
        """
        上传文件到OSS
        :param local_file_path: 本地文件路径
        :param object_name: OSS对象名称（如：recordings/20240115_xxx.mp3）
        :return: OSS文件URL
        """
        if not self.use_oss:
            raise Exception("未配置阿里云OSS，请在.env文件中配置OSS相关信息")

        try:
            logger.info(f"开始上传文件到OSS: {local_file_path} -> {object_name}")

            # 上传文件
            result = self.bucket.put_object_from_file(object_name, local_file_path)

            if result.status != 200:
                raise Exception(f"OSS上传失败，状态码: {result.status}")

            # 返回公开访问URL
            url = f"{self.base_url}/{object_name}"
            logger.info(f"文件上传成功: {url}")

            return url

        except oss2.exceptions.OssError as e:
            logger.error(f"OSS上传失败: {e}")
            raise Exception(f"OSS上传失败: {str(e)}")
        except Exception as e:
            logger.error(f"文件上传异常: {e}")
            raise Exception(f"文件上传异常: {str(e)}")

    def delete_file(self, object_name: str) -> bool:
        """
        删除OSS文件
        :param object_name: OSS对象名称
        :return: 是否删除成功
        """
        if not self.use_oss:
            return False

        try:
            self.bucket.delete_object(object_name)
            logger.info(f"OSS文件删除成功: {object_name}")
            return True
        except Exception as e:
            logger.error(f"OSS文件删除失败: {e}")
            return False

    def generate_object_name(self, original_filename: str) -> str:
        """
        生成OSS对象名称
        :param original_filename: 原始文件名
        :return: OSS对象名称
        """
        import uuid
        from datetime import datetime

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        ext = original_filename.split('.')[-1]

        return f"recordings/{timestamp}_{unique_id}.{ext}"

    def extract_object_name_from_url(self, url: str) -> str:
        """
        从URL中提取对象名称
        :param url: OSS文件URL
        :return: 对象名称
        """
        if not url or not self.base_url:
            return ""

        return url.replace(f"{self.base_url}/", "")


# 创建全局实例
oss_uploader = OSSUploader()