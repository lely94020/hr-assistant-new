"""
创建带真实文件的测试简历数据
"""
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.resume import Resume
from app.crud.resume import save_uploaded_file
from io import BytesIO

def create_test_resumes():
    """创建测试简历数据"""

    # 创建表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 创建上传目录
        upload_dir = "../uploads/resumes"
        os.makedirs(upload_dir, exist_ok=True)

        # 创建简单的测试文本文件（模拟简历）
        test_resumes = [
            {
                "candidate_name": "张三",
                "phone": "13812345678",
                "email": "zhangsan@example.com",
                "education": "本科",
                "school": "北京大学",
                "major": "计算机科学",
                "work_years": 5,
                "current_company": "阿里巴巴",
                "current_position": "高级Java工程师",
                "skills": ["Java", "Spring Boot", "MySQL"],
                "status": 1,
                "parse_status": 2,
                "content": "张三的简历内容..."
            },
            {
                "candidate_name": "李四",
                "phone": "13987654321",
                "email": "lisi@example.com",
                "education": "硕士",
                "school": "清华大学",
                "major": "软件工程",
                "work_years": 3,
                "current_company": "腾讯",
                "current_position": "Python工程师",
                "skills": ["Python", "Django", "PostgreSQL"],
                "status": 2,
                "parse_status": 2,
                "content": "李四的简历内容..."
            }
        ]

        for resume_data in test_resumes:
            # 创建测试文件
            filename = f"{resume_data['candidate_name']}_简历.txt"
            filepath = os.path.join(upload_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(resume_data.pop('content'))

            # 创建简历记录
            resume = Resume(
                candidate_name=resume_data['candidate_name'],
                phone=resume_data['phone'],
                email=resume_data['email'],
                education=resume_data['education'],
                school=resume_data['school'],
                major=resume_data['major'],
                work_years=resume_data['work_years'],
                current_company=resume_data['current_company'],
                current_position=resume_data['current_position'],
                skills=resume_data['skills'],
                file_path=filepath,
                file_name=filename,
                file_type='txt',
                file_size=os.path.getsize(filepath),
                status=resume_data['status'],
                parse_status=resume_data['parse_status'],
                is_deleted=0
            )

            db.add(resume)
            print(f"✅ 创建简历: {resume_data['candidate_name']}")

        db.commit()
        print(f"\n🎉 成功创建 {len(test_resumes)} 条测试简历")

    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_resumes()