"""
Milvus 向量数据库客户端（单例）
统一管理 Milvus 连接、集合、插入、检索和删除操作
"""
import warnings
from typing import List, Optional

try:
    from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False


class MilvusClient:
    """Milvus 客户端单例"""

    _instance = None

    HOST = "localhost"
    PORT = "19530"
    COLLECTION_NAME = "resumes"
    DIMENSION = 1536

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def is_available(self) -> bool:
        return MILVUS_AVAILABLE

    def connect(self) -> bool:
        """连接 Milvus（已初始化则跳过）"""
        if not MILVUS_AVAILABLE:
            print("警告: pymilvus 未安装，向量搜索功能不可用")
            return False
        if self._initialized:
            return True
        try:
            connections.connect(host=self.HOST, port=self.PORT)
            self._initialized = True
            print("✅ Milvus 连接成功")
            return True
        except Exception as e:
            print(f"Milvus 连接失败: {e}")
            return False

    def ensure_collection(self) -> bool:
        """确保集合存在，不存在则创建"""
        if not self.connect():
            return False
        try:
            if utility.has_collection(self.COLLECTION_NAME):
                return True
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="resume_id", dtype=DataType.INT64, description="简历ID"),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.DIMENSION),
                FieldSchema(name="candidate_name", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="skills", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="content_hash", dtype=DataType.VARCHAR, max_length=100),
            ]
            schema = CollectionSchema(fields, description="简历向量集合")
            collection = Collection(self.COLLECTION_NAME, schema)
            collection.create_index("embedding", {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            })
            print(f"✅ 创建 Milvus 集合: {self.COLLECTION_NAME}")
            return True
        except Exception as e:
            print(f"创建 Milvus 集合失败: {e}")
            return False

    def get_collection(self) -> Optional["Collection"]:
        """获取已加载的集合对象"""
        if not self.ensure_collection():
            return None
        collection = Collection(self.COLLECTION_NAME)
        collection.load()
        return collection

    def insert(self, resume_id: int, embedding: list,
               candidate_name: str = "unknown", skills: str = "") -> str:
        """插入向量并返回 Milvus ID"""
        collection = self.get_collection()
        if not collection:
            return ""
        entities = [[resume_id], [embedding], [candidate_name], [skills], [""]]
        result = collection.insert(entities)
        collection.flush()
        return str(result.primary_keys[0])

    def search(self, query_vector: list, top_k: int = 20,
               output_fields: Optional[list] = None) -> list:
        """执行向量检索"""
        collection = self.get_collection()
        if not collection:
            return []
        if output_fields is None:
            output_fields = ["resume_id"]
        params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            results = collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=params,
                limit=top_k,
                output_fields=output_fields
            )
        return results

    def delete(self, milvus_id: str) -> bool:
        """根据 Milvus ID 删除向量"""
        collection = self.get_collection()
        if not collection:
            return False
        collection.delete(f"id == {milvus_id}")
        collection.flush()
        return True

    def batch_delete(self, milvus_ids: List[str]) -> bool:
        """批量删除向量"""
        if not milvus_ids:
            return False
        collection = self.get_collection()
        if not collection:
            return False
        id_list = ", ".join(milvus_ids)
        collection.delete(f"id in [{id_list}]")
        collection.flush()
        return True

    def close(self):
        """断开连接"""
        if self._initialized:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", DeprecationWarning)
                    connections.disconnect("default")
                self._initialized = False
                print("✅ Milvus 连接已关闭")
            except Exception as e:
                print(f"关闭 Milvus 连接失败: {e}")
