from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base


class InterviewRecording(Base):
    """面试录音表"""
    __tablename__ = "interview_recording"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    resume_id = Column(BigInteger, nullable=False, comment="关联简历/候选人ID")
    position_id = Column(BigInteger, nullable=True, comment="关联岗位ID")
    file_name = Column(String(200), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_type = Column(String(10), nullable=False, comment="文件类型：mp3/wav/m4a/aac")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    duration = Column(Integer, nullable=True, comment="录音时长(秒)")
    transcript = Column(Text, nullable=True, comment="转换后的文字稿")
    transcript_status = Column(SmallInteger, nullable=False, default=0, comment="转写状态：0-未转写 1-转写中 2-已完成 3-转写失败")
    transcript_error = Column(String(500), nullable=True, comment="转写失败原因")
    interviewer = Column(String(50), nullable=True, comment="面试官姓名")
    interview_date = Column(Date, nullable=True, comment="面试日期")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")