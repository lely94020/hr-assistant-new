# debug_api.py
"""
调试API响应，检查数据格式
运行方式: python debug_api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.crud import position as position_crud
from app.crud import resume as resume_crud


def debug_api():
    """调试API响应"""
    db = SessionLocal()

    try:
        print("="*60)
        print("🔍 调试岗位列表API")
        print("="*60)

        # 模拟API调用
        total, positions = position_crud.get_position_list(
            db, page=1, page_size=100,
            position_name=None, department=None, status=None
        )

        print(f"总数: {total}")
        print(f"返回数量: {len(positions)}")

        if positions:
            print("\n前3条岗位数据:")
            for pos in positions[:3]:
                print(f"  ID: {pos.id}")
                print(f"  名称: {pos.position_name}")
                print(f"  部门: {pos.department}")
                print(f"  状态: {pos.status}")
                print()
        else:
            print("\n⚠️  没有岗位数据\n")

        print("="*60)
        print("🔍 调试简历列表API")
        print("="*60)

        # 模拟API调用
        resume_result = resume_crud.get_resumes(
            db,
            keyword=None,
            position_id=None,
            education=None,
            work_years_min=None,
            work_years_max=None,
            status=None,
            page=1,
            page_size=100
        )

        print(f"总数: {resume_result['total']}")
        print(f"返回数量: {len(resume_result['items'])}")

        if resume_result['items']:
            print("\n前3条简历数据:")
            for res in resume_result['items'][:3]:
                print(f"  ID: {res.id}")
                print(f"  姓名: {res.candidate_name}")
                print(f"  学历: {res.education}")
                print(f"  工作年限: {res.work_years}")
                print()
        else:
            print("\n⚠️  没有简历数据\n")

    finally:
        db.close()


if __name__ == "__main__":
    debug_api()
