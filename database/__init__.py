"""
数据库模块

包含数据库相关的所有功能：
- mysql: MySQL数据库实现
- config: 数据库配置
"""

from .mysql import ConversationDatabase
from .config import DB_CONFIG

__all__ = ['ConversationDatabase', 'DB_CONFIG']
