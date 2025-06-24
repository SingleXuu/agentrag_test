"""
工具基类和枚举定义
"""

import inspect
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict

class ToolCategory(Enum):
    """工具分类枚举"""
    WEATHER = "weather"
    CALCULATION = "calculation"
    SEARCH = "search"
    TRANSLATION = "translation"
    CODE = "code"
    TIME = "time"
    SYSTEM = "system"
    CUSTOM = "custom"

class ToolPermission(Enum):
    """工具权限级别"""
    PUBLIC = "public"      # 所有agent都可以使用
    RESTRICTED = "restricted"  # 需要特定权限
    ADMIN = "admin"       # 仅管理员agent

class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 category: ToolCategory = ToolCategory.CUSTOM,
                 permission: ToolPermission = ToolPermission.PUBLIC):
        self.name = name
        self.description = description
        self.category = category
        self.permission = permission
        self.usage_count = 0
        self.last_used = None
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> str:
        """执行工具功能"""
        pass
    
    def get_signature(self) -> Dict:
        """获取工具的函数签名"""
        sig = inspect.signature(self.execute)
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                param.name: {
                    "type": str(param.annotation) if param.annotation != param.empty else "str",
                    "required": param.default == param.empty
                }
                for param in sig.parameters.values()
                if param.name not in ['self', 'args', 'kwargs']
            }
        }
    
    async def __call__(self, *args, **kwargs) -> str:
        """调用工具并记录使用情况"""
        self.usage_count += 1
        self.last_used = datetime.now()
        return await self.execute(*args, **kwargs)
