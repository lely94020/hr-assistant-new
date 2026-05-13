from pymilvus import MilvusClient

# 连接本地 Milvus
client = MilvusClient(
    uri="http://localhost:19530"
)

print("✅ 新版 Milvus 连接成功，无任何警告！")