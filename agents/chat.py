"""
AgentChat主类 - 多Agent聊天管理器
"""

import asyncio
import json
from typing import Dict, List, Optional, AsyncGenerator, Any, Callable
from datetime import datetime
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage, AssistantMessage

from .types import AgentType
from .config import AgentConfig
from database import ConversationDatabase, DB_CONFIG
from tools import tools_manager, ToolCategory, ToolPermission

class AgentChat:
    """
    Multi-agent chat manager with tools and memory functionality.
    
    This class manages multiple specialized AI agents, each with their own
    conversation context, tools, and persistent memory stored in MySQL database.
    
    Features:
    - Multiple specialized agent management
    - Persistent conversation memory (MySQL)
    - Tool integration per agent
    - Streaming responses
    - Agent switching and specialization
    - Conversation history management
    """
    
    def __init__(self, model_client: OpenAIChatCompletionClient, conversation_id: str = "default"):
        """
        Initialize the AgentChat manager.
        
        Args:
            model_client: OpenAI compatible model client
            conversation_id: Unique identifier for this conversation
        """
        self.model_client = model_client
        self.conversation_id = conversation_id
        self.agents: Dict[AgentType, AssistantAgent] = {}
        self.current_agent_type = AgentType.GENERAL
        self.db = ConversationDatabase(**DB_CONFIG)
        self.conversation_history: List[Dict] = []
    
    def _get_tools_for_agent(self, agent_type: AgentType) -> List[Callable]:
        """为指定agent类型获取工具"""
        # 根据agent类型获取相应的工具分类
        tool_categories = AgentConfig.get_agent_tool_categories(agent_type)
        
        # 从工具管理器获取工具
        available_tools = tools_manager.get_available_tools(
            categories=tool_categories,
            permissions=[ToolPermission.PUBLIC, ToolPermission.RESTRICTED]
        )
        
        # 获取工具名称列表
        tool_names = [tool.name for tool in available_tools]
        
        # 返回工具函数
        return tools_manager.get_tool_functions(tool_names)

    async def _get_history_context(self) -> str:
        """获取历史对话上下文字符串（备用方案）"""
        try:
            # 获取最近5条消息作为上下文
            history_messages = await self.db.get_recent_messages(self.conversation_id, limit=5)

            if not history_messages:
                return ""

            context_lines = []
            for msg in history_messages:
                role_name = "用户" if msg["role"] == "user" else "助手"
                context_lines.append(f"{role_name}: {msg['content']}")

            return "\n".join(context_lines)

        except Exception as e:
            print(f"⚠️ 获取历史上下文失败: {e}")
            return ""

    async def _get_history_context(self) -> str:
        """获取历史对话上下文字符串"""
        try:
            # 获取最近5条消息作为上下文
            history_messages = await self.db.get_recent_messages(self.conversation_id, limit=5)

            if not history_messages:
                return ""

            context_lines = []
            for msg in history_messages:
                role_name = "用户" if msg["role"] == "user" else "助手"
                context_lines.append(f"{role_name}: {msg['content']}")

            return "\n".join(context_lines)

        except Exception as e:
            print(f"⚠️ 获取历史上下文失败: {e}")
            return ""
    
    async def _create_agent(self, agent_type: AgentType) -> AssistantAgent:
        """创建指定类型的agent"""
        config = AgentConfig.get_agent_config(agent_type)

        # 从工具管理器获取该agent类型对应的工具
        tools = self._get_tools_for_agent(agent_type)

        # 获取历史消息用于系统提示
        history_context = await self._get_history_context()

        # 如果有历史记录，将其添加到系统消息中
        system_message = config["system_message"]
        if history_context:
            system_message += f"\n\n## 对话历史上下文\n{history_context}\n\n请基于以上历史记录继续对话。"

        agent = AssistantAgent(
            name=f"{config['name']}_{self.conversation_id}",
            model_client=self.model_client,
            # tools=tools,
            system_message=system_message,
            reflect_on_tool_use=True,
            model_client_stream=True,
        )

        # 尝试加载历史记忆（如果支持）
        await self._load_agent_memory(agent)

        print(f"🤖 创建了 {agent_type.value} agent，包含 {len(tools)} 个工具")

        return agent
    
    async def _load_agent_memory(self, agent: AssistantAgent):
        """为agent加载历史记忆"""
        try:
            # 从数据库加载最近20条消息
            history_messages = await self.db.get_recent_messages(self.conversation_id, limit=20)

            if history_messages:
                print(f"📚 为agent加载了 {len(history_messages)} 条历史消息")

                # 将历史消息转换为AutoGen消息格式
                context_messages = []
                for msg in history_messages:
                    if msg["role"] == "user":
                        context_messages.append(
                            UserMessage(content=msg["content"], source="user")
                        )
                    elif msg["role"] == "assistant":
                        context_messages.append(
                            AssistantMessage(content=msg["content"], source="assistant")
                        )

                # 尝试使用正确的方法加载历史消息
                try:
                    if hasattr(agent, '_add_messages_to_context'):
                        # 使用正确的方法名
                        await agent._add_messages_to_context(context_messages)
                        print(f"✅ 成功加载 {len(context_messages)} 条历史消息到Agent上下文")
                    else:
                        print("⚠️ Agent不支持 _add_messages_to_context 方法，使用系统消息方式")

                except Exception as history_error:
                    print(f"⚠️ 历史消息加载失败，但Agent创建成功: {history_error}")
                    # 即使历史加载失败，也不影响Agent的正常使用

        except Exception as e:
            print(f"⚠️ 加载历史消息时出错: {e}")
    
    async def get_agent(self, agent_type: AgentType) -> AssistantAgent:
        """获取或创建指定类型的agent"""
        if agent_type not in self.agents:
            print(f"🤖 创建新的 {agent_type.value} agent")
            self.agents[agent_type] = await self._create_agent(agent_type)
        
        return self.agents[agent_type]
    
    async def switch_agent(self, agent_type: AgentType):
        """切换到指定类型的agent"""
        self.current_agent_type = agent_type
        print(f"🔄 切换到 {agent_type.value} agent")
    
    def _detect_agent_type(self, message: str) -> AgentType:
        """根据消息内容自动检测应该使用的agent类型"""
        message_lower = message.lower()
        
        # 天气相关关键词
        weather_keywords = ["天气", "温度", "下雨", "晴天", "阴天", "weather", "temperature"]
        if any(keyword in message_lower for keyword in weather_keywords):
            return AgentType.WEATHER
        
        # 计算相关关键词
        calc_keywords = ["计算", "算", "+", "-", "*", "/", "=", "数学", "math"]
        if any(keyword in message_lower for keyword in calc_keywords):
            return AgentType.CALCULATOR
        
        # 搜索相关关键词
        search_keywords = ["搜索", "查找", "search", "find", "查询"]
        if any(keyword in message_lower for keyword in search_keywords):
            return AgentType.SEARCH
        
        # 翻译相关关键词
        translate_keywords = ["翻译", "translate", "英文", "中文", "日文"]
        if any(keyword in message_lower for keyword in translate_keywords):
            return AgentType.TRANSLATOR
        
        # 编程相关关键词
        code_keywords = ["代码", "编程", "python", "javascript", "code", "程序"]
        if any(keyword in message_lower for keyword in code_keywords):
            return AgentType.CODER
        
        return AgentType.GENERAL
    
    async def initialize_database(self):
        """初始化数据库连接"""
        await self.db.init_database()
    
    async def save_message(self, role: str, content: str):
        """保存消息到数据库"""
        await self.db.save_message(self.conversation_id, role, content)
    
    async def get_conversation_history(self, limit: int = 50) -> List[Dict]:
        """获取会话历史"""
        return await self.db.get_recent_messages(self.conversation_id, limit)
    
    async def clear_conversation(self):
        """清除当前会话"""
        await self.db.delete_conversation(self.conversation_id)
        # 清除内存中的agents
        self.agents.clear()
        print(f"🗑️ 已清除会话 {self.conversation_id}")
    
    async def process_message(self, message: str, auto_detect: bool = True) -> AsyncGenerator[str, None]:
        """
        处理用户消息并返回流式响应

        Args:
            message: 用户消息
            auto_detect: 是否自动检测agent类型

        Yields:
            str: AI回复的文本片段
        """
        try:
            # 保存用户消息
            await self.save_message("user", message)

            # 自动检测agent类型（如果启用）
            if auto_detect:
                detected_type = self._detect_agent_type(message)
                if detected_type != self.current_agent_type:
                    await self.switch_agent(detected_type)
            
            # 获取当前agent
            current_agent = await self.get_agent(self.current_agent_type)
            
            # 处理消息并获取流式响应
            response_text = ""
            async for response in current_agent.run_stream(task=message):
                if hasattr(response, 'content') and response.content:
                    chunk = response.content
                    response_text += chunk
                    yield chunk
            
            # 保存AI回复
            if response_text:
                await self.save_message("assistant", response_text)
                
        except Exception as e:
            error_msg = f"处理消息时出错: {str(e)}"
            print(f"❌ {error_msg}")
            yield error_msg
    
    async def get_available_agents(self) -> List[str]:
        """获取可用的agent类型列表"""
        return [agent_type.value for agent_type in AgentType]
    
    async def get_agent_info(self, agent_type: AgentType) -> Dict:
        """获取agent信息"""
        config = AgentConfig.get_agent_config(agent_type)
        
        # 获取该agent可用的工具
        tool_categories = AgentConfig.get_agent_tool_categories(agent_type)
        available_tools = tools_manager.get_available_tools(categories=tool_categories)
        tool_names = [tool.name for tool in available_tools]
        
        return {
            "type": agent_type.value,
            "name": config["name"],
            "tools": tool_names,
            "tool_categories": [cat.value for cat in tool_categories],
            "description": config["system_message"][:100] + "..."
        }
    
    async def get_tools_info(self) -> Dict:
        """获取工具管理器信息"""
        return tools_manager.get_tools_info()
    
    async def get_tools_usage_stats(self) -> Dict:
        """获取工具使用统计"""
        return tools_manager.get_usage_stats()
    
    async def get_available_tool_categories(self) -> List[str]:
        """获取可用的工具分类"""
        return [category.value for category in ToolCategory]
    
    async def get_tools_by_category(self, category: str) -> List[Dict]:
        """按分类获取工具"""
        try:
            cat_enum = ToolCategory(category)
            tools = tools_manager.get_tools_by_category(cat_enum)
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category.value,
                    "permission": tool.permission.value,
                    "usage_count": tool.usage_count
                }
                for tool in tools
            ]
        except ValueError:
            return []
    
    async def close(self):
        """关闭资源"""
        await self.db.close_connection_pool()
        print("👋 AgentChat 已关闭")
