"""
RAG检索模块
"""

import time
from typing import List, Dict, Any, Optional
from .models import QueryRequest, QueryResponse, DocumentInfo
from .vector import VectorStore

class RAGRetriever:
    """RAG检索器"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.documents = {}  # document_id -> DocumentInfo
    
    def add_document(self, doc_info: DocumentInfo):
        """添加文档信息"""
        self.documents[doc_info.id] = doc_info
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        """执行RAG查询"""
        start_time = time.time()
        
        # 执行向量搜索
        search_results = await self.vector_store.search(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        # 过滤指定文档（如果有）
        if request.document_ids:
            search_results = [
                result for result in search_results
                if result["metadata"]["document_id"] in request.document_ids
            ]
        
        # 格式化结果
        formatted_results = []
        for result in search_results:
            doc_id = result["metadata"]["document_id"]
            doc_info = self.documents.get(doc_id)
            
            formatted_result = {
                "chunk_id": result["chunk_id"],
                "content": result["content"],
                "similarity": result["similarity"],
                "document_id": doc_id,
                "document_name": doc_info.original_name if doc_info else "Unknown",
                "chunk_index": result["metadata"]["chunk_index"],
                "metadata": result["metadata"]
            }
            formatted_results.append(formatted_result)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results),
            processing_time=processing_time
        )
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """获取指定文档的所有块"""
        chunks = []
        for chunk_id, metadata in self.vector_store.metadata.items():
            if metadata["document_id"] == document_id:
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": self.vector_store.chunks[chunk_id],
                    "chunk_index": metadata["chunk_index"],
                    "metadata": metadata
                })
        
        # 按块索引排序
        chunks.sort(key=lambda x: x["chunk_index"])
        return chunks
    
    async def delete_document(self, document_id: str):
        """删除文档"""
        await self.vector_store.delete_document(document_id)
        self.documents.pop(document_id, None)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取检索器统计信息"""
        vector_stats = await self.vector_store.get_stats()
        
        return {
            "total_documents": len(self.documents),
            "total_chunks": vector_stats["total_chunks"],
            "vector_dimension": vector_stats["dimension"],
            "documents": [
                {
                    "id": doc.id,
                    "name": doc.original_name,
                    "status": doc.status.value,
                    "chunk_count": doc.chunk_count
                }
                for doc in self.documents.values()
            ]
        }
