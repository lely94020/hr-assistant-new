# create_question_table.py
"""
创建面试题表的脚本
运行方式: python create_question_table.py
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models.question import InterviewQuestion


def create_table():
    """创建面试题表"""
    print("正在创建面试题表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 面试题表创建成功")
        print(f"表名: {InterviewQuestion.__tablename__}")
    except Exception as e:
        print(f"❌ 创建失败: {str(e)}")
        raise


if __name__ == "__main__":
    create_table()
