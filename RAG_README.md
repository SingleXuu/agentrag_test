# 📚 RAG模块使用说明

## 🎯 功能概述

RAG (Retrieval-Augmented Generation) 模块为AI助手系统提供了文档上传、处理、向量化和检索功能。

### ✨ 主要特性

- **📁 文件上传**: 支持拖拽上传、点击上传
- **📊 实时进度**: 上传和处理进度实时显示
- **🔍 智能检索**: 基于向量相似度的文档检索
- **📄 多格式支持**: PDF, DOCX, TXT, MD, HTML
- **💾 状态管理**: 完整的文档生命周期管理

## 🏗️ 模块结构

```
rag/
├── __init__.py          # 模块初始化
├── models.py            # 数据模型定义
├── document.py          # 文档处理器
├── vector.py            # 向量存储器
├── retrieval.py         # RAG检索器
└── api.py              # API端点
```

## 🚀 快速开始

### 1. 启动应用

```bash
python main.py
```

### 2. 访问RAG页面

打开浏览器访问：http://localhost:8000/rag

### 3. 上传文档

- **拖拽上传**: 直接将文件拖拽到上传区域
- **点击上传**: 点击"选择文件"按钮选择文件
- **支持格式**: PDF, DOCX, TXT, MD, HTML
- **大小限制**: 最大10MB

### 4. 查询文档

在查询框中输入问题，系统会在已上传的文档中搜索相关内容。

## 📊 API端点

### 文档上传
```http
POST /rag/upload
Content-Type: multipart/form-data

file: <文件>
```

### 查询状态
```http
GET /rag/status/{document_id}
```

### 文档查询
```http
POST /rag/query
Content-Type: application/json

{
    "query": "查询内容",
    "top_k": 5,
    "similarity_threshold": 0.7
}
```

### 文档列表
```http
GET /rag/documents
```

### 删除文档
```http
DELETE /rag/documents/{document_id}
```

## 🔧 扩展开发

### 添加新的文档类型

1. 在 `models.py` 中添加新的文档类型：
```python
class DocumentType(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    XLSX = "xlsx"  # 新增
```

2. 在 `document.py` 中实现提取逻辑：
```python
async def _extract_from_xlsx(self, file_path: str) -> str:
    # 实现Excel文件文本提取
    pass
```

### 集成真实的向量化模型

在 `vector.py` 中替换模拟的嵌入生成：

```python
async def _generate_embedding(self, text: str) -> List[float]:
    # 使用 sentence-transformers
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text)
    return embedding.tolist()
```

### 添加持久化存储

当前向量存储在内存中，可以集成：
- **Chroma**: 轻量级向量数据库
- **Pinecone**: 云端向量数据库
- **Weaviate**: 开源向量搜索引擎

## 🎨 前端自定义

### 修改样式

编辑 `rag_upload.html` 中的CSS样式：

```css
.upload-area {
    border: 3px dashed #your-color;
    background: #your-background;
}
```

### 添加新功能

在 `static/rag-upload.js` 中添加新的JavaScript功能：

```javascript
class RAGUploadManager {
    // 添加新方法
    async customFunction() {
        // 自定义功能实现
    }
}
```

## 🔍 待实现功能

以下功能框架已搭建，需要具体实现：

### 1. PDF文本提取
```python
# 在 document.py 中
async def _extract_from_pdf(self, file_path: str) -> str:
    # TODO: 使用 PyPDF2 或 pdfplumber
    import PyPDF2
    # 实现PDF文本提取逻辑
```

### 2. DOCX文档处理
```python
# 在 document.py 中
async def _extract_from_docx(self, file_path: str) -> str:
    # TODO: 使用 python-docx
    from docx import Document
    # 实现DOCX文本提取逻辑
```

### 3. HTML内容提取
```python
# 在 document.py 中
async def _extract_from_html(self, file_path: str) -> str:
    # TODO: 使用 BeautifulSoup
    from bs4 import BeautifulSoup
    # 实现HTML文本提取逻辑
```

### 4. 真实向量嵌入
```python
# 在 vector.py 中
async def _generate_embedding(self, text: str) -> List[float]:
    # TODO: 集成真实的嵌入模型
    # 选项1: OpenAI Embeddings
    # 选项2: Sentence Transformers
    # 选项3: 本地模型
```

## 📦 推荐依赖

根据需要添加以下依赖到 `requirements.txt`：

```txt
# PDF处理
PyPDF2>=3.0.1
pdfplumber>=0.9.0

# DOCX处理
python-docx>=0.8.11

# HTML处理
beautifulsoup4>=4.12.2
lxml>=4.9.3

# 向量化
sentence-transformers>=2.2.2
openai>=1.0.0

# 向量数据库
chromadb>=0.4.0
pinecone-client>=2.2.4
```

## 🧪 测试

### 单元测试
```bash
# 测试文档处理
python -m pytest tests/test_document.py

# 测试向量存储
python -m pytest tests/test_vector.py

# 测试检索功能
python -m pytest tests/test_retrieval.py
```

### 集成测试
```bash
# 测试完整RAG流程
python -m pytest tests/test_rag_integration.py
```

## 🔧 配置选项

可以通过环境变量配置RAG模块：

```bash
# 上传目录
export RAG_UPLOAD_DIR="uploads"

# 最大文件大小 (MB)
export RAG_MAX_FILE_SIZE=10

# 向量维度
export RAG_VECTOR_DIMENSION=768

# 分块大小
export RAG_CHUNK_SIZE=1000

# 分块重叠
export RAG_CHUNK_OVERLAP=200
```

## 🎉 总结

RAG模块提供了完整的文档处理和检索框架，您可以：

1. **直接使用**: 基本功能已经可用
2. **逐步完善**: 根据需要实现具体的文档处理逻辑
3. **自由扩展**: 添加新的文档类型和功能
4. **集成升级**: 使用更强大的向量化和存储方案

框架设计遵循模块化原则，每个组件都可以独立开发和测试！🚀
