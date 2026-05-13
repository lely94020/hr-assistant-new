# check_data.py
"""
检查数据库中是否有岗位和简历数据
运行方式: python check_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.position import JobPosition
from app.models.resume import Resume


def check_data():
    """检查数据"""
    db = SessionLocal()

    try:
        # 检查岗位数据
        positions = db.query(JobPosition).filter(JobPosition.is_deleted == 0).all()
        print(f"\n📋 岗位数量: {len(positions)}")
        if positions:
            for pos in positions[:5]:
                print(f"  - ID: {pos.id}, 名称: {pos.position_name}, 部门: {pos.department}")
        else:
            print("  ⚠️  数据库中没有岗位数据！")
            print("  💡 请先在'岗位管理'页面创建岗位")

        # 检查简历数据
        resumes = db.query(Resume).filter(Resume.is_deleted == 0).all()
        print(f"\n📄 简历数量: {len(resumes)}")
        if resumes:
            for res in resumes[:5]:
                print(f"  - ID: {res.id}, 姓名: {res.candidate_name}, 学历: {res.education}")
        else:
            print("  ⚠️  数据库中没有简历数据！")
            print("  💡 请先在'简历管理'页面上传简历")

        print("\n" + "="*50)

    finally:
        db.close()


if __name__ == "__main__":
    check_data()
