"""
文档处理模块
"""

import os
import uuid
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import DocumentInfo, DocumentType, DocumentStatus, DocumentChunk

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        """确保上传目录存在"""
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> DocumentInfo:
        """保存上传的文件"""
        # 生成唯一文件ID
        doc_id = str(uuid.uuid4())
        
        # 确定文件类型
        file_ext = filename.lower().split('.')[-1]
        try:
            file_type = DocumentType(file_ext)
        except ValueError:
            raise ValueError(f"不支持的文件类型: {file_ext}")
        
        # 生成存储文件名
        stored_filename = f"{doc_id}.{file_ext}"
        file_path = os.path.join(self.upload_dir, stored_filename)
        
        # 异步保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # 创建文档信息
        doc_info = DocumentInfo(
            id=doc_id,
            filename=stored_filename,
            original_name=filename,
            file_size=len(file_content),
            file_type=file_type,
            status=DocumentStatus.UPLOADING,
            upload_time=datetime.now()
        )
        
        return doc_info
    
    async def process_document(self, doc_info: DocumentInfo) -> List[DocumentChunk]:
        """处理文档，提取文本并分块"""
        try:
            # 更新状态为处理中
            doc_info.status = DocumentStatus.PROCESSING
            
            # 读取文件内容
            file_path = os.path.join(self.upload_dir, doc_info.filename)
            content = await self._extract_text(file_path, doc_info.file_type)
            
            # 分块处理
            chunks = await self._split_text(content, doc_info.id)
            
            # 更新文档信息
            doc_info.status = DocumentStatus.COMPLETED
            doc_info.process_time = datetime.now()
            doc_info.chunk_count = len(chunks)
            
            return chunks
            
        except Exception as e:
            doc_info.status = DocumentStatus.FAILED
            doc_info.error_message = str(e)
            raise
    
    async def _extract_text(self, file_path: str, file_type: DocumentType) -> str:
        """从文件中提取文本"""
        if file_type == DocumentType.TXT:
            return await self._extract_from_txt(file_path)
        elif file_type == DocumentType.PDF:
            return await self._extract_from_pdf(file_path)
        elif file_type == DocumentType.DOCX:
            return await self._extract_from_docx(file_path)
        elif file_type == DocumentType.MD:
            return await self._extract_from_markdown(file_path)
        elif file_type == DocumentType.HTML:
            return await self._extract_from_html(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    
    async def _extract_from_txt(self, file_path: str) -> str:
        """从TXT文件提取文本"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """从PDF文件提取文本"""
        # TODO: 实现PDF文本提取
        # 可以使用 PyPDF2, pdfplumber 等库
        return "PDF文本提取功能待实现"
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """从DOCX文件提取文本"""
        # TODO: 实现DOCX文本提取
        # 可以使用 python-docx 库
        return "DOCX文本提取功能待实现"
    
    async def _extract_from_markdown(self, file_path: str) -> str:
        """从Markdown文件提取文本"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # TODO: 可以使用 markdown 库解析
        # 这里简单返回原始内容
        return content
    
    async def _extract_from_html(self, file_path: str) -> str:
        """从HTML文件提取文本"""
        # TODO: 实现HTML文本提取
        # 可以使用 BeautifulSoup 库
        return "HTML文本提取功能待实现"
    
    async def _split_text(self, text: str, document_id: str, chunk_size: int = 1000, overlap: int = 200) -> List[DocumentChunk]:
        """将文本分块"""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            # 尝试在句号处分割，避免截断句子
            if end < len(text) and '。' in chunk_text:
                last_period = chunk_text.rfind('。')
                if last_period > chunk_size // 2:  # 确保块不会太小
                    end = start + last_period + 1
                    chunk_text = text[start:end]
            
            chunk = DocumentChunk(
                id=f"{document_id}_chunk_{chunk_index}",
                document_id=document_id,
                content=chunk_text.strip(),
                chunk_index=chunk_index,
                metadata={
                    "start_pos": start,
                    "end_pos": end,
                    "length": len(chunk_text)
                }
            )
            
            chunks.append(chunk)
            chunk_index += 1
            start = end - overlap  # 重叠部分
        
        return chunks
    
    async def delete_document(self, doc_info: DocumentInfo):
        """删除文档文件"""
        file_path = os.path.join(self.upload_dir, doc_info.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
