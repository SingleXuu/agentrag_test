/**
 * RAG文档上传系统前端脚本
 */

class RAGUploadManager {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.progressList = document.getElementById('progressList');
        this.documentList = document.getElementById('documentList');
        this.queryInput = document.getElementById('queryInput');
        this.queryResults = document.getElementById('queryResults');
        
        this.uploadingFiles = new Map(); // 跟踪上传中的文件
        this.documents = new Map(); // 存储文档信息
        
        this.initEventListeners();
        this.loadDocuments();
        
        // 定期更新进度
        setInterval(() => this.updateProgress(), 2000);
    }

    initEventListeners() {
        // 文件选择
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // 拖拽上传
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // 点击上传区域
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // 查询输入框回车
        this.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.queryDocuments();
            }
        });
    }

    async handleFiles(files) {
        for (let file of files) {
            if (this.validateFile(file)) {
                await this.uploadFile(file);
            }
        }
    }

    validateFile(file) {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                             'text/plain', 'text/markdown', 'text/html'];
        const allowedExtensions = ['.pdf', '.docx', '.txt', '.md', '.html'];
        
        // 检查文件大小 (10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showError(`文件 ${file.name} 超过10MB大小限制`);
            return false;
        }

        // 检查文件类型
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.includes(fileExtension)) {
            this.showError(`不支持的文件类型: ${file.name}`);
            return false;
        }

        return true;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            // 显示上传进度
            const progressId = this.addProgressItem(file.name, 'uploading', 0);
            
            const response = await fetch('/rag/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`上传失败: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.success) {
                // 更新进度状态
                this.updateProgressItem(progressId, 'processing', 10, '文件上传成功，正在处理...');
                
                // 跟踪文档ID
                this.uploadingFiles.set(result.document_id, {
                    progressId: progressId,
                    filename: file.name
                });

                this.showSuccess(`文件 ${file.name} 上传成功`);
            } else {
                throw new Error(result.message || '上传失败');
            }

        } catch (error) {
            this.showError(`上传 ${file.name} 失败: ${error.message}`);
            this.removeProgressItem(progressId);
        }
    }

    addProgressItem(filename, status, progress) {
        const progressId = 'progress_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        const progressHTML = `
            <div class="progress-item" id="${progressId}">
                <div class="progress-header">
                    <span class="file-name">${filename}</span>
                    <span class="file-status status-${status}">${this.getStatusText(status)}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">进度: ${progress}%</div>
            </div>
        `;
        
        this.progressList.insertAdjacentHTML('beforeend', progressHTML);
        return progressId;
    }

    updateProgressItem(progressId, status, progress, message = '') {
        const item = document.getElementById(progressId);
        if (!item) return;

        const statusElement = item.querySelector('.file-status');
        const progressFill = item.querySelector('.progress-fill');
        const progressText = item.querySelector('.progress-text');

        statusElement.className = `file-status status-${status}`;
        statusElement.textContent = this.getStatusText(status);
        progressFill.style.width = `${progress}%`;
        progressText.textContent = message || `进度: ${progress}%`;
    }

    removeProgressItem(progressId) {
        const item = document.getElementById(progressId);
        if (item) {
            item.remove();
        }
    }

    getStatusText(status) {
        const statusMap = {
            'uploading': '上传中',
            'processing': '处理中',
            'completed': '完成',
            'failed': '失败'
        };
        return statusMap[status] || status;
    }

    async updateProgress() {
        for (let [documentId, fileInfo] of this.uploadingFiles) {
            try {
                const response = await fetch(`/rag/status/${documentId}`);
                if (response.ok) {
                    const status = await response.json();
                    
                    this.updateProgressItem(
                        fileInfo.progressId,
                        status.status,
                        status.progress,
                        status.message
                    );

                    // 如果处理完成或失败，从跟踪列表中移除
                    if (status.status === 'completed' || status.status === 'failed') {
                        this.uploadingFiles.delete(documentId);
                        
                        // 3秒后移除进度条
                        setTimeout(() => {
                            this.removeProgressItem(fileInfo.progressId);
                        }, 3000);

                        // 重新加载文档列表
                        this.loadDocuments();
                    }
                }
            } catch (error) {
                console.error('更新进度失败:', error);
            }
        }
    }

    async loadDocuments() {
        try {
            const response = await fetch('/rag/documents');
            if (response.ok) {
                const data = await response.json();
                this.displayDocuments(data.documents);
            }
        } catch (error) {
            console.error('加载文档列表失败:', error);
        }
    }

    displayDocuments(documents) {
        this.documentList.innerHTML = '';
        
        if (documents.length === 0) {
            this.documentList.innerHTML = '<p style="text-align: center; color: #666;">暂无文档</p>';
            return;
        }

        documents.forEach(doc => {
            const docHTML = `
                <div class="document-item">
                    <div class="document-info">
                        <div class="document-name">${doc.filename}</div>
                        <div class="document-meta">
                            大小: ${this.formatFileSize(doc.file_size)} | 
                            类型: ${doc.file_type.toUpperCase()} | 
                            状态: ${this.getStatusText(doc.status)} |
                            块数: ${doc.chunk_count || 0} |
                            上传时间: ${new Date(doc.upload_time).toLocaleString()}
                        </div>
                        ${doc.error_message ? `<div style="color: #dc3545; font-size: 0.8em;">${doc.error_message}</div>` : ''}
                    </div>
                    <div class="document-actions">
                        <button class="btn btn-danger" onclick="ragManager.deleteDocument('${doc.id}')">
                            删除
                        </button>
                    </div>
                </div>
            `;
            this.documentList.insertAdjacentHTML('beforeend', docHTML);
        });
    }

    async deleteDocument(documentId) {
        if (!confirm('确定要删除这个文档吗？')) {
            return;
        }

        try {
            const response = await fetch(`/rag/documents/${documentId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccess('文档删除成功');
                this.loadDocuments();
            } else {
                throw new Error('删除失败');
            }
        } catch (error) {
            this.showError(`删除文档失败: ${error.message}`);
        }
    }

    async queryDocuments() {
        const query = this.queryInput.value.trim();
        if (!query) {
            this.showError('请输入查询内容');
            return;
        }

        try {
            this.queryResults.innerHTML = '<div class="loading">🔍 搜索中...</div>';

            const response = await fetch('/rag/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    top_k: 5,
                    similarity_threshold: 0.3
                })
            });

            if (!response.ok) {
                throw new Error('查询失败');
            }

            const result = await response.json();
            this.displayQueryResults(result);

        } catch (error) {
            this.queryResults.innerHTML = `<div style="color: #dc3545;">查询失败: ${error.message}</div>`;
        }
    }

    displayQueryResults(result) {
        this.queryResults.innerHTML = '';

        if (result.results.length === 0) {
            this.queryResults.innerHTML = '<div style="text-align: center; color: #666;">未找到相关内容</div>';
            return;
        }

        const headerHTML = `
            <div style="margin-bottom: 15px; color: #666;">
                找到 ${result.total_results} 个相关结果 (耗时: ${result.processing_time.toFixed(3)}s)
            </div>
        `;
        this.queryResults.insertAdjacentHTML('beforeend', headerHTML);

        result.results.forEach((item, index) => {
            const resultHTML = `
                <div class="result-item">
                    <div class="result-content">${this.highlightQuery(item.content, result.query)}</div>
                    <div class="result-meta">
                        文档: ${item.document_name} | 
                        相似度: ${(item.similarity * 100).toFixed(1)}% |
                        块索引: ${item.chunk_index}
                    </div>
                </div>
            `;
            this.queryResults.insertAdjacentHTML('beforeend', resultHTML);
        });
    }

    highlightQuery(content, query) {
        // 简单的关键词高亮
        const regex = new RegExp(`(${query})`, 'gi');
        return content.replace(regex, '<mark style="background: #fff3cd;">$1</mark>');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            max-width: 300px;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // 自动移除
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// 初始化管理器
const ragManager = new RAGUploadManager();

// 全局函数（供HTML调用）
function queryDocuments() {
    ragManager.queryDocuments();
}
