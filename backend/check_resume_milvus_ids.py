"""
检查数据库中简历的 milvus_id
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.resume import Resume

def check_milvus_ids():
    """检查简历的 milvus_id"""

    db = SessionLocal()

    try:
        # 查询所有未删除的简历
        resumes = db.query(Resume).filter(Resume.is_deleted == 0).all()

        print(f"📊 数据库中共有 {len(resumes)} 条简历\n")

        if len(resumes) == 0:
            print("⚠️  数据库中没有任何简历数据")
            print("💡 请先上传简历，或运行 create_sample_resumes.py 创建测试数据")
            return

        has_milvus = 0
        no_milvus = 0

        print("=" * 100)
        print(f"{'ID':<5} {'姓名':<10} {'Milvus ID':<20} {'解析状态':<10} {'状态'}")
        print("=" * 100)

        for resume in resumes:
            if resume.milvus_id:
                has_milvus += 1
                status = "✅ 已向量化"
            else:
                no_milvus += 1
                status = "❌ 未向量化"

            parse_status_map = {
                0: "未解析",
                1: "解析中",
                2: "成功",
                3: "失败"
            }
            parse_status = parse_status_map.get(resume.parse_status, "未知")

            print(f"{resume.id:<5} {resume.candidate_name:<10} "
                  f"{str(resume.milvus_id or 'None'):<20} "
                  f"{parse_status:<10} {status}")

        print("=" * 100)
        print(f"\n📈 统计:")
        print(f"   - 已向量化: {has_milvus} 条")
        print(f"   - 未向量化: {no_milvus} 条")
        print(f"   - 总计: {len(resumes)} 条")

        if no_milvus > 0:
            print(f"\n💡 提示: 有 {no_milvus} 条简历未向量化")
            if has_milvus == 0:
                print("   可能原因:")
                print("   1. Milvus 服务在上传时未启动")
                print("   2. 向量化过程出错（检查后端日志）")
                print("   3. 使用了 create_sample_resumes.py（该脚本不触发向量化）")

    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_milvus_ids()
