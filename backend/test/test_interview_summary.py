"""
测试面试摘要生成功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.interview_summary_service import generate_interview_summary


def test_generate_summary():
    """测试生成面试摘要"""
    db = SessionLocal()
    try:
        # 使用一个已存在的录音ID进行测试
        recording_id = 10  # 请根据实际情况修改

        print(f"开始为录音 ID={recording_id} 生成面试摘要...")

        summary = generate_interview_summary(recording_id, db)

        print("✅ 摘要生成成功！")
        print("\n=== 面试概览 ===")
        print(summary["summary_overview"])

        print("\n=== 技术能力 ===")
        for skill in summary["technical_skills"]:
            print(f"- {skill}")

        print("\n=== 软技能 ===")
        for skill in summary["soft_skills"]:
            print(f"- {skill}")

        print("\n=== 亮点 ===")
        highlights = summary["highlights"].split('\n') if summary["highlights"] else []
        for highlight in highlights:
            if highlight.strip():
                print(f"- {highlight}")

        print("\n=== 疑虑 ===")
        concerns = summary["concerns"].split('\n') if summary["concerns"] else []
        for concern in concerns:
            if concern.strip():
                print(f"- {concern}")

        print("\n=== 核心问答 ===")
        for qa in summary["key_qa"]:
            print(f"Q: {qa['question']}")
            print(f"A: {qa['answer_summary']}")
            print(f"质量: {qa['answer_quality']}")
            print()

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_generate_summary()