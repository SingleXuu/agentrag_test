"""
RAG模块的数据模型
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(Enum):
    """文档处理状态"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(Enum):
    """支持的文档类型"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"

class DocumentInfo(BaseModel):
    """文档信息模型"""
    id: str
    filename: str
    original_name: str
    file_size: int
    file_type: DocumentType
    status: DocumentStatus
    upload_time: datetime
    process_time: Optional[datetime] = None
    error_message: Optional[str] = None
    chunk_count: Optional[int] = None
    metadata: Dict[str, Any] = {}

class UploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    document_id: str
    message: str
    filename: str

class ProcessingStatus(BaseModel):
    """处理状态响应"""
    document_id: str
    status: DocumentStatus
    progress: int  # 0-100
    message: str
    chunk_count: Optional[int] = None

class QueryRequest(BaseModel):
    """查询请求"""
    query: str
    document_ids: Optional[List[str]] = None  # 指定文档范围
    top_k: int = 5
    similarity_threshold: float = 0.7

class QueryResponse(BaseModel):
    """查询响应"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    processing_time: float

class DocumentChunk(BaseModel):
    """文档块模型"""
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
