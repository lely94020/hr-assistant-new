"""
检查 Milvus 中的简历向量数据
"""
from pymilvus import connections, Collection, utility

def check_milvus_data():
    """检查 Milvus 中的简历数据"""

    COLLECTION_NAME = "resumes"

    try:
        # 1. 连接 Milvus
        print("📡 连接 Milvus...")
        connections.connect(host="localhost", port="19530")
        print("✅ 连接成功")

        # 2. 检查集合是否存在
        if not utility.has_collection(COLLECTION_NAME):
            print(f"❌ 集合 '{COLLECTION_NAME}' 不存在")
            print("💡 提示：可能需要先上传简历才会创建集合")
            return

        print(f"✅ 集合 '{COLLECTION_NAME}' 存在")

        # 3. 加载集合
        collection = Collection(COLLECTION_NAME)
        collection.load()

        # 4. 获取数据统计
        entity_count = collection.num_entities
        print(f"\n📊 集合中的向量数量: {entity_count}")

        if entity_count == 0:
            print("⚠️  集合为空，还没有简历向量数据")
            return

        # 5. 查询所有数据（限制显示前10条）
        print("\n📋 前10条简历向量数据:")
        print("-" * 80)

        results = collection.query(
            expr="id >= 0",
            output_fields=["resume_id", "candidate_name", "skills"],
            limit=10
        )

        for i, result in enumerate(results, 1):
            print(f"{i}. ID: {result['id']}, "
                  f"简历ID: {result['resume_id']}, "
                  f"姓名: {result.get('candidate_name', 'N/A')}, "
                  f"技能: {result.get('skills', 'N/A')[:50]}")

        print("-" * 80)

        # 6. 检查索引
        indexes = collection.indexes
        print(f"\n📑 索引信息:")
        for index in indexes:
            print(f"   - 字段: {index.field_name}, "
                  f"类型: {index.params.get('index_type', 'N/A')}")

        # 7. 统计信息
        print(f"\n📈 集合统计:")
        print(f"   - 总实体数: {entity_count}")
        print(f"   - 索引数量: {len(indexes)}")

    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        connections.disconnect("default")

if __name__ == "__main__":
    check_milvus_data()