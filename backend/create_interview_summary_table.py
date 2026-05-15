"""
创建面试摘要表的脚本
"""
from app.database import engine
from app.models.interview_summary import InterviewSummary
from sqlalchemy import inspect


def create_interview_summary_table():
    """创建面试摘要表"""
    print("正在创建面试摘要表...")

    # 检查表是否已存在
    inspector = inspect(engine)
    if "interview_summary" in inspector.get_table_names():
        print("面试摘要表已存在")
        return

    # 创建表
    InterviewSummary.__table__.create(engine)
    print("✅ 面试摘要表创建完成")


if __name__ == "__main__":
    create_interview_summary_table()