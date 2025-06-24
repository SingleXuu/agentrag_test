"""
工具系统包

这个包包含了所有工具相关的模块：
- base: 工具基类和枚举
- manager: 工具管理器
- builtin: 内置工具
- custom: 自定义工具
"""

from .base import BaseTool, ToolCategory, ToolPermission
from .manager import ToolsManager, tools_manager
from .builtin import *
from .custom import *

__all__ = [
    'BaseTool',
    'ToolCategory', 
    'ToolPermission',
    'ToolsManager',
    'tools_manager',
    'register_custom_tool',
    'get_tools_for_agent'
]

def register_custom_tool(tool: BaseTool):
    """注册自定义工具的便捷函数"""
    tools_manager.register_tool(tool)

def get_tools_for_agent(categories: list = None) -> list:
    """为agent获取工具函数的便捷函数"""
    if categories:
        category_enums = [ToolCategory(cat) for cat in categories if cat in [c.value for c in ToolCategory]]
        available_tools = tools_manager.get_available_tools(categories=category_enums)
    else:
        available_tools = tools_manager.get_available_tools()
    
    tool_names = [tool.name for tool in available_tools]
    return tools_manager.get_tool_functions(tool_names)
