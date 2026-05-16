"""
检查数据库中的简历和评价数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.crud.resume import get_resumes
from app.crud.interview_evaluation import get_evaluations_by_resume_id


def check_data():
    """检查数据库中的数据"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("检查简历数据")
        print("=" * 60)
        
        # 获取所有简历
        result = get_resumes(db, page=1, page_size=100)
        resumes = result['items']
        
        if not resumes:
            print("✗ 数据库中没有简历数据")
            return
        
        print(f"\n找到 {len(resumes)} 份简历:\n")
        for resume in resumes:
            print(f"ID: {resume.id}")
            print(f"  姓名: {resume.candidate_name}")
            print(f"  当前职位: {resume.current_position or '未指定'}")
            print(f"  学历: {resume.education or '未指定'}")
            print(f"  工作年限: {resume.work_years or '未指定'}年")
            print(f"  手机: {resume.phone or '未指定'}")
            print()
        
        print("=" * 60)
        print("检查评价数据")
        print("=" * 60)
        
        for resume in resumes:
            evaluations = get_evaluations_by_resume_id(db, resume.id)
            print(f"\n简历 ID={resume.id} ({resume.candidate_name}):")
            if evaluations:
                print(f"  评价数量: {len(evaluations)}")
                for eval_item in evaluations:
                    print(f"    - 评价ID: {eval_item.id}, 得分: {eval_item.total_score}, 推荐: {eval_item.recommendation}")
            else:
                print("  暂无评价")
        
        print("\n" + "=" * 60)
        print("建议的测试命令")
        print("=" * 60)
        if resumes:
            first_resume_id = resumes[0].id
            print(f"\n使用第一个简历ID进行测试: {first_resume_id}")
            print(f"\nPython测试脚本:")
            print(f"  python test_evaluation_api.py {first_resume_id}")
            print(f"\n前端访问URL:")
            print(f"  http://localhost:5173/evaluation?resumeId={first_resume_id}")
        
    finally:
        db.close()


if __name__ == "__main__":
    check_data()