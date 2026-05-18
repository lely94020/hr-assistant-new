from sqlalchemy.orm import Session
from app.crud.resume import create_resume, save_uploaded_file
from app.schemas.resume import ResumeCreate
from typing import List, Dict, Any
import os
import re
from datetime import datetime

# 文档解析库
import PyPDF2
import pdfplumber
from docx import Document

# AI相关 - 使用新版LangChain API
from langchain_community.chat_models import ChatTongyi
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.embeddings import DashScopeEmbeddings

# 配置
import json

# 导入Milvus
try:
    from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
    MILVUS_AVAILABLE = True
    print("✅ Milvus 客户端导入成功")
except ImportError:
    MILVUS_AVAILABLE = False
    print("⚠️ pymilvus未安装，向量搜索功能将不可用")


class ResumeService:
    """简历服务类"""

    # Milvus配置
    MILVUS_HOST = "localhost"
    MILVUS_PORT = "19530"
    COLLECTION_NAME = "resumes"

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析PDF文件内容"""
        text_content = ""
        
        try:
            # 方法1: 使用pdfplumber（更适合中文）
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            # 如果pdfplumber提取的内容太少，尝试PyPDF2
            if len(text_content.strip()) < 50:
                text_content = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")
        
        return text_content.strip()

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """解析Word文件内容"""
        text_content = ""
        
        try:
            doc = Document(file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text.strip())
            text_content = "\n".join(paragraphs)
        except Exception as e:
            raise Exception(f"Word文档解析失败: {str(e)}")
        
        return text_content.strip()

    @staticmethod
    async def parse_resume_content(file_path: str, file_type: str) -> str:
        """解析简历文件内容（PDF/Word）"""
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")
        
        if file_type.lower() == 'pdf':
            return ResumeService.parse_pdf(file_path)
        elif file_type.lower() in ['docx', 'doc']:
            return ResumeService.parse_docx(file_path)
        else:
            raise Exception(f"不支持的文件格式: {file_type}")

    @staticmethod
    async def extract_resume_info(text_content: str) -> Dict[str, Any]:
        """使用AI提取简历结构化信息"""
        try:
            # 初始化通义千问LLM（新版API）
            llm = ChatTongyi(
                model="qwen-plus",
                temperature=0.1,
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
            
            # 构建Prompt
            prompt_template = """你是一个专业的简历解析助手。请从以下简历文本中提取结构化信息。

简历内容：
{text}

请以JSON格式返回以下字段（如果某个字段无法提取，请设置为null）：
{{
  "candidate_name": "候选人姓名",
  "phone": "手机号",
  "email": "邮箱",
  "education": "最高学历（如：本科、硕士、博士）",
  "school": "毕业院校",
  "major": "专业",
  "work_years": "工作年限（数字）",
  "current_company": "当前公司",
  "current_position": "当前职位",
  "skills": ["技能标签数组"],
  "work_experience": [
    {{
      "company": "公司名称",
      "position": "职位",
      "duration": "工作时间段",
      "description": "工作描述"
    }}
  ],
  "project_experience": [
    {{
      "name": "项目名称",
      "role": "担任角色",
      "description": "项目描述"
    }}
  ],
  "education_experience": [
    {{
      "school": "学校名称",
      "degree": "学位",
      "major": "专业",
      "duration": "就读时间"
    }}
  ],
  "resume_summary": "用一句话总结候选人的核心优势和特点"
}}

只返回JSON，不要有其他文字说明。确保JSON格式正确。"""
            
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # 创建链：Prompt -> LLM -> JSON解析
            chain = prompt | llm | JsonOutputParser()
            
            # 调用AI提取信息（使用异步方法）
            extracted_info = await chain.ainvoke({"text": text_content[:5000]})
            
            # 数据清洗和验证
            extracted_info = ResumeService._clean_extracted_data(extracted_info)
            
            return extracted_info
            
        except Exception as e:
            print(f"AI提取失败，使用规则提取: {str(e)}")
            # 降级方案：使用正则表达式提取
            return ResumeService._fallback_extract(text_content)

    @staticmethod
    def _fallback_extract(text_content: str) -> Dict[str, Any]:
        """降级方案：使用正则表达式提取基本信息"""
        info = {}
        
        # 提取手机号
        phone_pattern = r'1[3-9]\d{9}'
        phone_match = re.search(phone_pattern, text_content)
        info['phone'] = phone_match.group() if phone_match else None
        
        # 提取邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text_content)
        info['email'] = email_match.group() if email_match else None
        
        # 提取姓名（简单规则：第一行或包含"姓名"的行）
        lines = text_content.split('\n')
        info['candidate_name'] = lines[0].strip() if lines else "未知"
        
        # 其他字段设为默认值
        info['education'] = None
        info['school'] = None
        info['major'] = None
        info['work_years'] = None
        info['current_company'] = None
        info['current_position'] = None
        info['skills'] = []
        info['work_experience'] = []
        info['project_experience'] = []
        info['education_experience'] = []
        info['resume_summary'] = ""
        
        return info

    @staticmethod
    def _clean_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗和验证提取的数据"""
        cleaned = {}
        
        # 基本字段
        cleaned['candidate_name'] = data.get('candidate_name') or "未知"
        cleaned['phone'] = data.get('phone')
        cleaned['email'] = data.get('email')
        cleaned['education'] = data.get('education')
        cleaned['school'] = data.get('school')
        cleaned['major'] = data.get('major')
        
        # 工作年限转换为整数
        work_years = data.get('work_years')
        if work_years is not None:
            try:
                cleaned['work_years'] = int(work_years)
            except (ValueError, TypeError):
                cleaned['work_years'] = None
        else:
            cleaned['work_years'] = None
        
        cleaned['current_company'] = data.get('current_company')
        cleaned['current_position'] = data.get('current_position')
        
        # 技能列表
        skills = data.get('skills', [])
        cleaned['skills'] = skills if isinstance(skills, list) else []
        
        # 经历列表
        cleaned['work_experience'] = data.get('work_experience', []) or []
        cleaned['project_experience'] = data.get('project_experience', []) or []
        cleaned['education_experience'] = data.get('education_experience', []) or []
        
        # 摘要
        cleaned['resume_summary'] = data.get('resume_summary', '')
        
        return cleaned

    @staticmethod
    def _init_milvus():
        """初始化Milvus连接"""
        if not MILVUS_AVAILABLE:
            print("警告: Milvus不可用，跳过向量存储")
            return False
        
        try:
            connections.connect(
                host=ResumeService.MILVUS_HOST,
                port=ResumeService.MILVUS_PORT
            )
            print("✅ Milvus 连接成功")
            return True
        except Exception as e:
            print(f"Milvus连接失败: {str(e)}")
            return False

    @staticmethod
    def _create_collection_if_not_exists():
        """创建集合（如果不存在）"""
        if not MILVUS_AVAILABLE:
            return False
        
        try:
            if utility.has_collection(ResumeService.COLLECTION_NAME):
                return True
            
            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="resume_id", dtype=DataType.INT64, description="简历ID"),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
                FieldSchema(name="candidate_name", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="skills", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="content_hash", dtype=DataType.VARCHAR, max_length=100)
            ]
            
            # 创建schema
            schema = CollectionSchema(fields, description="简历向量集合")
            
            # 创建集合
            collection = Collection(ResumeService.COLLECTION_NAME, schema)
            
            # 创建索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            collection.create_index("embedding", index_params)
            
            print(f"✅ 创建Milvus集合: {ResumeService.COLLECTION_NAME}")
            return True
            
        except Exception as e:
            print(f"创建Milvus集合失败: {str(e)}")
            return False

    @staticmethod
    async def vectorize_resume(text_content: str, resume_id: int = 0) -> str:
        """将简历内容向量化并存储到Milvus"""
        if not MILVUS_AVAILABLE:
            print("警告: Milvus不可用，跳过向量化")
            return ""
        
        try:
            # 初始化Milvus
            if not ResumeService._init_milvus():
                return ""
            
            ResumeService._create_collection_if_not_exists()
            
            # 生成embedding
            embeddings = DashScopeEmbeddings(
                model="text-embedding-v1",
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
            
            # 对文本进行embedding
            embedding = embeddings.embed_query(text_content)
            
            # 插入到Milvus
            collection = Collection(ResumeService.COLLECTION_NAME)
            
            entities = [
                [resume_id],  # resume_id
                [embedding],  # embedding
                ["unknown"],  # candidate_name (暂时未知)
                [""],  # skills
                [""]  # content_hash
            ]
            
            insert_result = collection.insert(entities)
            collection.flush()
            
            # 返回milvus_id
            milvus_id = str(insert_result.primary_keys[0])
            return milvus_id
            
        except Exception as e:
            print(f"向量化失败: {str(e)}")
            # 如果Milvus不可用，返回空字符串，不影响主流程
            return ""

    @staticmethod
    def delete_milvus_vector(milvus_id: str) -> bool:
        """从Milvus中删除向量"""
        if not MILVUS_AVAILABLE:
            print("警告: Milvus不可用，跳过向量删除")
            return False
        
        try:
            if not ResumeService._init_milvus():
                return False
            
            collection = Collection(ResumeService.COLLECTION_NAME)
            collection.delete(f"id == {milvus_id}")
            collection.flush()
            print(f"✅ 删除Milvus向量: {milvus_id}")
            return True
            
        except Exception as e:
            print(f"删除Milvus向量失败: {str(e)}")
            return False

    @staticmethod
    async def process_single_resume(db: Session, file, position_id: int = None) -> Dict[str, Any]:
        """处理单个简历上传"""
        try:
            # 保存文件
            file_info = save_uploaded_file(file)

            # 解析简历内容
            text_content = await ResumeService.parse_resume_content(
                file_info["file_path"],
                file_info["file_type"]
            )

            # AI提取结构化信息
            extracted_info = await ResumeService.extract_resume_info(text_content)

            # 向量化存储（异步，不阻塞主流程）
            try:
                milvus_id = await ResumeService.vectorize_resume(text_content)
            except Exception as e:
                print(f"向量化失败，继续处理: {str(e)}")
                milvus_id = ""

            # 构建简历数据
            resume_data = ResumeCreate(
                candidate_name=extracted_info.get("candidate_name", "未知"),
                phone=extracted_info.get("phone"),
                email=extracted_info.get("email"),
                education=extracted_info.get("education"),
                school=extracted_info.get("school"),
                major=extracted_info.get("major"),
                work_years=extracted_info.get("work_years"),
                current_company=extracted_info.get("current_company"),
                current_position=extracted_info.get("current_position"),
                skills=extracted_info.get("skills"),
                work_experience=extracted_info.get("work_experience"),
                project_experience=extracted_info.get("project_experience"),
                education_experience=extracted_info.get("education_experience"),
                resume_summary=extracted_info.get("resume_summary"),
                original_content=text_content,
                file_path=file_info["file_path"],
                file_name=file_info["file_name"],
                file_type=file_info["file_type"],
                file_size=file_info["file_size"],
                milvus_id=milvus_id if milvus_id else None,
                position_id=position_id
            )

            # 保存到数据库
            resume = create_resume(db, resume_data)

            return {
                "file_name": file.filename,
                "status": "success",
                "resume_id": resume.id
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "file_name": file.filename,
                "status": "failed",
                "error": str(e)
            }

    @staticmethod
    async def process_batch_resumes(db: Session, files: list, position_id: int = None) -> Dict[str, Any]:
        """批量处理简历上传"""
        results = []
        success_count = 0
        failed_count = 0
        
        for file in files:
            result = await ResumeService.process_single_resume(db, file, position_id)
            results.append(result)
            
            if result["status"] == "success":
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "total": len(files),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }
