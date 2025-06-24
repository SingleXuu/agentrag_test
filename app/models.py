"""
API数据模型
"""

from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    agent_type: str = "auto"  # "auto" 或具体的agent类型
    auto_detect: bool = True

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent_type: str

class AgentSwitchRequest(BaseModel):
    conversation_id: str
    agent_type: str

class AgentInfo(BaseModel):
    type: str
    name: str
    tools: List[str]
    description: str
