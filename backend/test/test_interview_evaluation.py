"""
面试评价模块测试脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.interview_evaluation_service import generate_interview_evaluation
from app.crud.interview_evaluation import get_evaluations_by_resume_id


def test_generate_evaluation():
    """测试生成面试评价"""
    print("=" * 50)
    print("测试：生成面试评价")
    print("=" * 50)

    db = SessionLocal()
    try:
        summary_id = 1

        print(f"\n使用摘要ID: {summary_id}")
        evaluation = generate_interview_evaluation(summary_id, db)

        print("\n✓ 评价生成成功！")
        print(f"评价ID: {evaluation['id']}")
        print(f"简历ID: {evaluation['resume_id']}")
        print(f"综合得分: {evaluation['total_score']}")
        print(f"推荐等级: {evaluation['recommendation']}")

        print("\n各维度评分:")
        for dimension, data in evaluation['scores'].items():
            print(f"  - {dimension}: {data['score']}分")
            if data.get('comment'):
                print(f"    评语: {data['comment']}")

        if evaluation.get('ai_comment'):
            print(f"\nAI综合评语:\n{evaluation['ai_comment']}")

        if evaluation.get('key_strengths'):
            print(f"\n核心优势:")
            for strength in evaluation['key_strengths']:
                print(f"  • {strength}")

        if evaluation.get('improvement_areas'):
            print(f"\n待提升领域:")
            for area in evaluation['improvement_areas']:
                print(f"  • {area}")

        if evaluation.get('hiring_suggestion'):
            print(f"\n录用建议:\n{evaluation['hiring_suggestion']}")

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        return False
    finally:
        db.close()


def test_get_evaluation_history(resume_id: int):
    """测试获取评价历史"""
    print("\n" + "=" * 50)
    print(f"测试：获取简历 {resume_id} 的评价历史")
    print("=" * 50)

    db = SessionLocal()
    try:
        evaluations = get_evaluations_by_resume_id(db, resume_id)

        print(f"\n找到 {len(evaluations)} 条评价记录\n")

        for i, eval_item in enumerate(evaluations, 1):
            print(f"评价 {i}:")
            print(f"  ID: {eval_item.id}")
            print(f"  综合得分: {eval_item.total_score}")
            print(f"  推荐等级: {eval_item.recommendation}")
            print(f"  创建时间: {eval_item.created_at}")
            print()

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n开始测试面试评价模块...\n")

    success = test_generate_evaluation()

    if success:
        resume_id = 1
        test_get_evaluation_history(resume_id)

    print("\n测试完成！")