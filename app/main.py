"""
FastAPI主应用
"""

import asyncio
import json
from typing import AsyncGenerator, Dict

from autogen_core.models import ModelFamily
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from autogen_ext.models.openai import OpenAIChatCompletionClient
import uvicorn

from .models import ChatRequest, ChatResponse, AgentSwitchRequest
from agents import AgentChat, AgentType
from rag.api import router as rag_router

app = FastAPI(title="AI Assistant with Multi-Agent Chat", description="Advanced AI Assistant with Multiple Specialized Agents")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include RAG router
app.include_router(rag_router)

# Initialize the model client
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-f95b28efff5f434db7a3be957504b586",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": False
    }
)

# 会话管理：为每个conversation_id创建独立的AgentChat
conversation_chats: Dict[str, AgentChat] = {}

async def get_or_create_chat(conversation_id: str) -> AgentChat:
    """获取或创建指定会话的AgentChat"""
    if conversation_id not in conversation_chats:
        print(f"🆕 为会话 {conversation_id} 创建新的AgentChat")
        chat = AgentChat(model_client, conversation_id)
        await chat.initialize_database()
        conversation_chats[conversation_id] = chat
    
    return conversation_chats[conversation_id]

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    print("🚀 Multi-Agent AI Assistant 启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    for chat in conversation_chats.values():
        await chat.close()
    print("👋 Multi-Agent AI Assistant 已关闭")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/rag", response_class=HTMLResponse)
async def rag_page():
    """Serve the RAG upload page"""
    with open("rag_upload.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle chat requests with multi-agent support and streaming response"""
    try:
        print(f"💬 收到会话 {request.conversation_id} 的消息: {request.message}")
        print(f"🤖 请求agent类型: {request.agent_type}, 自动检测: {request.auto_detect}")
        
        # 获取或创建AgentChat
        chat = await get_or_create_chat(request.conversation_id)
        
        # 如果指定了特定的agent类型（非auto），则切换到该agent
        if request.agent_type != "auto":
            try:
                agent_type = AgentType(request.agent_type)
                await chat.switch_agent(agent_type)
                print(f"🔄 手动切换到 {agent_type.value} agent")
            except ValueError:
                print(f"⚠️ 未知的agent类型: {request.agent_type}，使用当前agent")
        
        async def generate_response() -> AsyncGenerator[str, None]:
            response_text = ""
            current_agent_type = chat.current_agent_type.value
            
            try:
                async for chunk in chat.process_message(request.message, auto_detect=request.auto_detect):
                    response_text += chunk
                    # Send each chunk as Server-Sent Events format
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False, 'agent_type': current_agent_type})}\n\n"
                
                # Send final message indicating completion
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_response': response_text, 'agent_type': current_agent_type})}\n\n"
                print(f"✅ 会话 {request.conversation_id} 回复完成，使用了 {current_agent_type} agent")
                
            except Exception as stream_error:
                print(f"❌ 流式处理错误: {stream_error}")
                error_msg = f"处理请求时出错: {str(stream_error)}"
                yield f"data: {json.dumps({'chunk': error_msg, 'done': True, 'error': True, 'agent_type': current_agent_type})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        print(f"❌ 会话 {request.conversation_id} 处理错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """Simple non-streaming chat endpoint with multi-agent support"""
    try:
        print(f"💬 收到简单会话 {request.conversation_id} 的消息: {request.message}")
        
        # 获取或创建AgentChat
        chat = await get_or_create_chat(request.conversation_id)
        
        # 如果指定了特定的agent类型，则切换到该agent
        if request.agent_type != "auto":
            try:
                agent_type = AgentType(request.agent_type)
                await chat.switch_agent(agent_type)
            except ValueError:
                pass  # 忽略无效的agent类型
        
        response_text = ""
        async for chunk in chat.process_message(request.message, auto_detect=request.auto_detect):
            response_text += chunk
        
        print(f"✅ 简单会话 {request.conversation_id} 回复完成")
        return ChatResponse(
            response=response_text,
            conversation_id=request.conversation_id,
            agent_type=chat.current_agent_type.value
        )
    except Exception as e:
        print(f"❌ 简单会话 {request.conversation_id} 处理错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_available_agents():
    """获取所有可用的agent类型"""
    try:
        # 创建临时chat实例来获取agent信息
        temp_chat = AgentChat(model_client, "temp")
        agents = await temp_chat.get_available_agents()
        
        agent_infos = []
        for agent_type in AgentType:
            info = await temp_chat.get_agent_info(agent_type)
            agent_infos.append(info)
        
        await temp_chat.close()
        
        return {
            "available_agents": agents,
            "agent_details": agent_infos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/switch")
async def switch_agent(request: AgentSwitchRequest):
    """切换指定会话的agent类型"""
    try:
        chat = await get_or_create_chat(request.conversation_id)
        
        try:
            agent_type = AgentType(request.agent_type)
            await chat.switch_agent(agent_type)
            
            return {
                "message": f"已切换到 {agent_type.value} agent",
                "conversation_id": request.conversation_id,
                "current_agent": agent_type.value
            }
        except ValueError:
            raise HTTPException(status_code=400, detail=f"未知的agent类型: {request.agent_type}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/agent")
async def get_current_agent(conversation_id: str):
    """获取指定会话当前使用的agent类型"""
    try:
        if conversation_id in conversation_chats:
            chat = conversation_chats[conversation_id]
            return {
                "conversation_id": conversation_id,
                "current_agent": chat.current_agent_type.value,
                "available_agents": await chat.get_available_agents()
            }
        else:
            return {
                "conversation_id": conversation_id,
                "current_agent": "general",  # 默认agent
                "available_agents": [agent_type.value for agent_type in AgentType]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str, limit: int = 50):
    """获取指定会话的历史记录"""
    try:
        chat = await get_or_create_chat(conversation_id)
        messages = await chat.get_conversation_history(limit)
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "total": len(messages),
            "current_agent": chat.current_agent_type.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """清除指定会话"""
    try:
        if conversation_id in conversation_chats:
            chat = conversation_chats[conversation_id]
            await chat.clear_conversation()
            await chat.close()
            del conversation_chats[conversation_id]
        
        return {"message": f"会话 {conversation_id} 已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_tools_info():
    """获取工具系统信息"""
    try:
        # 创建临时chat实例来获取工具信息
        temp_chat = AgentChat(model_client, "temp")
        tools_info = await temp_chat.get_tools_info()
        await temp_chat.close()
        
        return tools_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/categories")
async def get_tool_categories():
    """获取工具分类"""
    try:
        temp_chat = AgentChat(model_client, "temp")
        categories = await temp_chat.get_available_tool_categories()
        await temp_chat.close()
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/category/{category}")
async def get_tools_by_category(category: str):
    """按分类获取工具"""
    try:
        temp_chat = AgentChat(model_client, "temp")
        tools = await temp_chat.get_tools_by_category(category)
        await temp_chat.close()
        
        return {"category": category, "tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/stats")
async def get_tools_usage_stats():
    """获取工具使用统计"""
    try:
        temp_chat = AgentChat(model_client, "temp")
        stats = await temp_chat.get_tools_usage_stats()
        await temp_chat.close()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Multi-Agent AI Assistant is running",
        "active_conversations": len(conversation_chats),
        "available_agents": [agent_type.value for agent_type in AgentType]
    }

@app.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    try:
        stats = {
            "active_conversations": len(conversation_chats),
            "available_agents": len(AgentType),
            "agent_types": [agent_type.value for agent_type in AgentType]
        }
        
        # 统计每个会话使用的agent类型
        agent_usage = {}
        for conv_id, chat in conversation_chats.items():
            agent_type = chat.current_agent_type.value
            agent_usage[agent_type] = agent_usage.get(agent_type, 0) + 1
        
        stats["agent_usage"] = agent_usage
        
        # 添加工具统计
        if conversation_chats:
            temp_chat = list(conversation_chats.values())[0]
            tools_stats = await temp_chat.get_tools_usage_stats()
            stats["tools_usage"] = tools_stats
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 启动多Agent AI Assistant服务器...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
