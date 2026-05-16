"""
为现有简历补充向量化
"""
import asyncio
import sys
import os
from sqlalchemy.orm import Session

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.resume import Resume
from app.services.resume_service import ResumeService

async def vectorize_existing_resumes():
    """为没有 milvus_id 的简历补充向量化"""

    db = SessionLocal()

    try:
        # 查询所有未向量化的简历
        resumes = db.query(Resume).filter(
            Resume.is_deleted == 0,
            (Resume.milvus_id == None) | (Resume.milvus_id == ''),
            Resume.parse_status == 2  # 只处理解析成功的
        ).all()

        print(f"📊 找到 {len(resumes)} 条需要向量化的简历\n")

        if len(resumes) == 0:
            print("✅ 所有简历都已向量化")
            return

        success_count = 0
        failed_count = 0

        for i, resume in enumerate(resumes, 1):
            print(f"[{i}/{len(resumes)}] 处理: {resume.candidate_name} (ID: {resume.id})")

            try:
                # 检查是否有原始内容
                if not resume.original_content:
                    print(f"   ⚠️  跳过：没有原始内容")
                    failed_count += 1
                    continue

                # 向量化
                print(f"   🔄 正在向量化...")
                milvus_id = await ResumeService.vectorize_resume(
                    resume.original_content,
                    resume.id
                )

                if milvus_id:
                    # 更新数据库
                    resume.milvus_id = milvus_id
                    db.commit()
                    print(f"   ✅ 成功: milvus_id = {milvus_id}")
                    success_count += 1
                else:
                    print(f"   ❌ 失败：向量化返回空值")
                    failed_count += 1

            except Exception as e:
                print(f"   ❌ 失败: {str(e)}")
                failed_count += 1
                db.rollback()

        print(f"\n📈 完成统计:")
        print(f"   - 成功: {success_count} 条")
        print(f"   - 失败: {failed_count} 条")
        print(f"   - 总计: {len(resumes)} 条")

    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(vectorize_existing_resumes())
