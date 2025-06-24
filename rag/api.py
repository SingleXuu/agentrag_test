"""
RAG模块的API端点
"""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from .models import (
    DocumentInfo, UploadResponse, ProcessingStatus, 
    QueryRequest, QueryResponse, DocumentStatus
)
from .document import DocumentProcessor
from .vector import VectorStore
from .retrieval import RAGRetriever

# 创建路由器
router = APIRouter(prefix="/rag", tags=["RAG"])

# 全局实例（实际项目中应该使用依赖注入）
document_processor = DocumentProcessor()
vector_store = VectorStore()
rag_retriever = RAGRetriever(vector_store)

# 存储文档信息和处理状态
documents_db = {}  # document_id -> DocumentInfo
processing_status = {}  # document_id -> ProcessingStatus

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """上传文档文件"""
    try:
        # 检查文件大小（限制为10MB）
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="文件大小超过10MB限制")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件并创建文档信息
        doc_info = await document_processor.save_uploaded_file(file_content, file.filename)
        
        # 存储文档信息
        documents_db[doc_info.id] = doc_info
        rag_retriever.add_document(doc_info)
        
        # 初始化处理状态
        processing_status[doc_info.id] = ProcessingStatus(
            document_id=doc_info.id,
            status=DocumentStatus.UPLOADING,
            progress=0,
            message="文件上传完成，等待处理"
        )
        
        # 后台处理文档
        background_tasks.add_task(process_document_background, doc_info.id)
        
        return UploadResponse(
            success=True,
            document_id=doc_info.id,
            message="文件上传成功，正在处理中",
            filename=doc_info.original_name
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

async def process_document_background(document_id: str):
    """后台处理文档"""
    try:
        doc_info = documents_db[document_id]
        
        # 更新状态：开始处理
        processing_status[document_id].status = DocumentStatus.PROCESSING
        processing_status[document_id].progress = 10
        processing_status[document_id].message = "正在提取文本内容"
        
        # 处理文档
        chunks = await document_processor.process_document(doc_info)
        
        # 更新进度
        processing_status[document_id].progress = 50
        processing_status[document_id].message = "正在生成向量嵌入"
        
        # 添加到向量存储
        await vector_store.add_chunks(chunks)
        
        # 更新状态：完成
        processing_status[document_id].status = DocumentStatus.COMPLETED
        processing_status[document_id].progress = 100
        processing_status[document_id].message = "文档处理完成"
        processing_status[document_id].chunk_count = len(chunks)
        
        # 更新文档信息
        documents_db[document_id] = doc_info
        
    except Exception as e:
        # 更新状态：失败
        processing_status[document_id].status = DocumentStatus.FAILED
        processing_status[document_id].progress = 0
        processing_status[document_id].message = f"处理失败: {str(e)}"
        
        # 更新文档信息
        doc_info.status = DocumentStatus.FAILED
        doc_info.error_message = str(e)
        documents_db[document_id] = doc_info

@router.get("/status/{document_id}", response_model=ProcessingStatus)
async def get_processing_status(document_id: str):
    """获取文档处理状态"""
    if document_id not in processing_status:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return processing_status[document_id]

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """查询文档"""
    try:
        response = await rag_retriever.query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get("/documents")
async def list_documents():
    """获取所有文档列表"""
    documents = []
    for doc_info in documents_db.values():
        status_info = processing_status.get(doc_info.id)
        documents.append({
            "id": doc_info.id,
            "filename": doc_info.original_name,
            "file_size": doc_info.file_size,
            "file_type": doc_info.file_type.value,
            "status": doc_info.status.value,
            "upload_time": doc_info.upload_time.isoformat(),
            "chunk_count": doc_info.chunk_count,
            "progress": status_info.progress if status_info else 0,
            "error_message": doc_info.error_message
        })
    
    return {"documents": documents}

@router.get("/documents/{document_id}")
async def get_document_info(document_id: str):
    """获取文档详细信息"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    doc_info = documents_db[document_id]
    status_info = processing_status.get(document_id)
    
    # 获取文档块信息
    chunks = await rag_retriever.get_document_chunks(document_id)
    
    return {
        "document": {
            "id": doc_info.id,
            "filename": doc_info.original_name,
            "file_size": doc_info.file_size,
            "file_type": doc_info.file_type.value,
            "status": doc_info.status.value,
            "upload_time": doc_info.upload_time.isoformat(),
            "process_time": doc_info.process_time.isoformat() if doc_info.process_time else None,
            "chunk_count": doc_info.chunk_count,
            "error_message": doc_info.error_message
        },
        "processing": {
            "progress": status_info.progress if status_info else 0,
            "message": status_info.message if status_info else ""
        },
        "chunks": chunks[:5]  # 只返回前5个块作为预览
    }

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """删除文档"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    try:
        doc_info = documents_db[document_id]
        
        # 删除文件
        await document_processor.delete_document(doc_info)
        
        # 删除向量数据
        await rag_retriever.delete_document(document_id)
        
        # 删除记录
        documents_db.pop(document_id, None)
        processing_status.pop(document_id, None)
        
        return {"message": "文档删除成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@router.get("/stats")
async def get_rag_stats():
    """获取RAG系统统计信息"""
    try:
        stats = await rag_retriever.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.post("/test-query")
async def test_query(query: str = "测试查询"):
    """测试查询功能"""
    request = QueryRequest(query=query, top_k=3)
    return await query_documents(request)
