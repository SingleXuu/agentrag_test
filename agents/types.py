"""
Agent类型定义
"""

from enum import Enum

class AgentType(Enum):
    """Agent类型枚举"""
    GENERAL = "general"          # 通用助手
    WEATHER = "weather"          # 天气专家
    CALCULATOR = "calculator"    # 计算专家
    SEARCH = "search"           # 搜索专家
    TRANSLATOR = "translator"   # 翻译专家
    CODER = "coder"            # 编程助手
