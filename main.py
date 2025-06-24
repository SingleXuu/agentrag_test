#!/usr/bin/env python3
"""
AI Assistant 主启动文件

这是多Agent AI助手的主入口文件
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 启动多Agent AI Assistant服务器...")
    print("📍 服务器地址: http://localhost:8000")
    print("🌐 请打开浏览器并访问上述地址")
    print("⚡ 按Ctrl+C停止服务器")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 AI Assistant服务器已停止。再见！")
    except Exception as e:
        print(f"❌ 启动服务器时出错: {e}")
        exit(1)
