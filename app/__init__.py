"""
应用程序模块

包含FastAPI应用和相关配置
"""

from .main import app
from .models import ChatRequest, ChatResponse, AgentSwitchRequest

__all__ = ['app', 'ChatRequest', 'ChatResponse', 'AgentSwitchRequest']
