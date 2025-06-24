"""
向量存储模块
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from .models import DocumentChunk

class VectorStore:
    """向量存储器"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.vectors = {}  # chunk_id -> vector
        self.metadata = {}  # chunk_id -> metadata
        self.chunks = {}  # chunk_id -> chunk_content
    
    async def add_chunks(self, chunks: List[DocumentChunk]):
        """添加文档块到向量存储"""
        for chunk in chunks:
            # 生成向量嵌入
            embedding = await self._generate_embedding(chunk.content)
            
            # 存储向量和元数据
            self.vectors[chunk.id] = embedding
            self.metadata[chunk.id] = {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                **chunk.metadata
            }
            self.chunks[chunk.id] = chunk.content
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        # TODO: 实现真实的嵌入生成
        # 可以使用 sentence-transformers, OpenAI embeddings 等
        
        # 这里返回随机向量作为示例
        return np.random.random(self.dimension).tolist()
    
    async def search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """搜索相似文档块"""
        # 生成查询向量
        query_vector = await self._generate_embedding(query)
        
        # 计算相似度
        similarities = []
        for chunk_id, vector in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, vector)
            if similarity >= similarity_threshold:
                similarities.append({
                    "chunk_id": chunk_id,
                    "similarity": similarity,
                    "content": self.chunks[chunk_id],
                    "metadata": self.metadata[chunk_id]
                })
        
        # 按相似度排序
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def delete_document(self, document_id: str):
        """删除文档的所有向量"""
        chunk_ids_to_delete = [
            chunk_id for chunk_id, metadata in self.metadata.items()
            if metadata["document_id"] == document_id
        ]
        
        for chunk_id in chunk_ids_to_delete:
            self.vectors.pop(chunk_id, None)
            self.metadata.pop(chunk_id, None)
            self.chunks.pop(chunk_id, None)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取向量存储统计信息"""
        return {
            "total_chunks": len(self.vectors),
            "dimension": self.dimension,
            "documents": len(set(meta["document_id"] for meta in self.metadata.values()))
        }
    
    async def save_to_file(self, filepath: str):
        """保存向量存储到文件"""
        data = {
            "dimension": self.dimension,
            "vectors": self.vectors,
            "metadata": self.metadata,
            "chunks": self.chunks
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def load_from_file(self, filepath: str):
        """从文件加载向量存储"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.dimension = data["dimension"]
        self.vectors = data["vectors"]
        self.metadata = data["metadata"]
        self.chunks = data["chunks"]
