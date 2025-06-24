"""
Agent配置
"""

from typing import Dict, List
from .types import AgentType
from tools import ToolCategory

class AgentConfig:
    """Agent配置管理"""
    
    @staticmethod
    def get_agent_config(agent_type: AgentType) -> Dict:
        """获取不同类型agent的配置"""
        configs = {
            AgentType.GENERAL: {
                "name": "general_assistant",
                "system_message": """你是一个全能的AI助手。你可以帮助用户：
                - 回答各种问题
                - 获取天气信息
                - 进行数学计算
                - 搜索信息
                - 获取时间
                - 单位转换
                - 随机生成
                请友好、专业地回答用户的问题。"""
            },
            AgentType.WEATHER: {
                "name": "weather_expert",
                "system_message": """你是一个天气专家。专门提供：
                - 详细的天气信息
                - 天气趋势分析
                - 出行建议
                - 穿衣建议
                请用专业但易懂的方式回答天气相关问题。"""
            },
            AgentType.CALCULATOR: {
                "name": "math_expert",
                "system_message": """你是一个数学计算专家。专门处理：
                - 各种数学计算
                - 数学公式解释
                - 计算步骤说明
                - 数学概念解释
                - 单位转换
                请准确地进行计算并解释计算过程。"""
            },
            AgentType.SEARCH: {
                "name": "search_expert",
                "system_message": """你是一个信息搜索专家。专门提供：
                - 网络信息搜索
                - 信息整理和总结
                - 可靠来源推荐
                - 事实核查
                请提供准确、有用的搜索结果。"""
            },
            AgentType.TRANSLATOR: {
                "name": "translator",
                "system_message": """你是一个翻译专家。专门提供：
                - 多语言翻译
                - 语言学习建议
                - 文化背景解释
                - 语法纠正
                请提供准确、自然的翻译。"""
            },
            AgentType.CODER: {
                "name": "coding_assistant",
                "system_message": """你是一个编程助手。专门提供：
                - 代码审查和优化
                - 编程问题解答
                - 算法解释
                - 最佳实践建议
                - 文件操作
                请提供清晰、实用的编程建议。"""
            }
        }
        return configs.get(agent_type, configs[AgentType.GENERAL])
    
    @staticmethod
    def get_agent_tool_categories(agent_type: AgentType) -> List[ToolCategory]:
        """获取agent类型对应的工具分类"""
        category_mapping = {
            AgentType.GENERAL: [
                ToolCategory.WEATHER, 
                ToolCategory.CALCULATION, 
                ToolCategory.SEARCH, 
                ToolCategory.TIME,
                ToolCategory.CUSTOM
            ],
            AgentType.WEATHER: [ToolCategory.WEATHER, ToolCategory.TIME],
            AgentType.CALCULATOR: [ToolCategory.CALCULATION],
            AgentType.SEARCH: [ToolCategory.SEARCH],
            AgentType.TRANSLATOR: [ToolCategory.TRANSLATION],
            AgentType.CODER: [ToolCategory.CODE, ToolCategory.SYSTEM]
        }
        
        return category_mapping.get(agent_type, [ToolCategory.CUSTOM])
