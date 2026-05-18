from sqlalchemy import Column, BigInteger, String, Text, Integer, SmallInteger, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base


class Resume(Base):
    """简历表"""
    __tablename__ = "resume"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    candidate_name = Column(String(50), nullable=False, comment="候选人姓名")
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="邮箱")
    education = Column(String(20), comment="学历")
    school = Column(String(100), comment="毕业院校")
    major = Column(String(100), comment="专业")
    work_years = Column(Integer, comment="工作年限")
    current_company = Column(String(100), comment="当前公司")
    current_position = Column(String(100), comment="当前职位")
    skills = Column(JSON, comment="技能标签数组")
    work_experience = Column(JSON, comment="工作经历")
    project_experience = Column(JSON, comment="项目经验")
    education_experience = Column(JSON, comment="教育经历")
    resume_summary = Column(Text, comment="AI生成的简历摘要")
    original_content = Column(Text, comment="简历原始文本内容")
    file_path = Column(String(500), nullable=False, comment="原始文件存储路径")
    file_name = Column(String(200), nullable=False, comment="原始文件名")
    file_type = Column(String(10), nullable=False, comment="文件类型：pdf/docx/doc")
    file_size = Column(BigInteger, comment="文件大小(字节)")
    milvus_id = Column(String(100), comment="Milvus向量ID")
    position_id = Column(BigInteger, comment="关联岗位ID")
    status = Column(SmallInteger, nullable=False, default=1, comment="状态：1-待筛选 2-初筛通过 3-面试中 4-已录用 5-已淘汰")
    parse_status = Column(SmallInteger, nullable=False, default=0, comment="解析状态：0-未解析 1-解析中 2-成功 3-失败")
    is_deleted = Column(SmallInteger, nullable=False, default=0, comment="软删除标记：0-正常 1-已删除")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
