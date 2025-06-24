#!/usr/bin/env python3
"""
Agent系统测试
"""

import asyncio
from agents import AgentChat, AgentType
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def test_agent_chat():
    """测试AgentChat的各种功能"""
    print("🚀 开始测试AgentChat...")
    
    # 初始化模型客户端
    model_client = OpenAIChatCompletionClient(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-f95b28efff5f434db7a3be957504b586",
    )
    
    # 创建AgentChat实例
    chat = AgentChat(model_client, conversation_id="test_multi_agent")
    
    try:
        # 初始化数据库
        await chat.initialize_database()
        print("✅ 数据库初始化完成")
        
        # 测试1: 自动agent检测
        print("\n🧪 测试1: 自动agent检测")
        test_messages = [
            "北京今天天气怎么样？",  # 应该切换到天气agent
            "帮我计算 25 * 37 + 100",  # 应该切换到计算agent
            "你好，请介绍一下自己"  # 应该使用通用agent
        ]
        
        for message in test_messages:
            print(f"\n👤 用户: {message}")
            print(f"🤖 AI回复: ", end="")
            
            async for chunk in chat.process_message(message, auto_detect=True):
                print(chunk, end="", flush=True)
            print()  # 换行

        # 测试2: 手动切换agent
        print("\n🧪 测试2: 手动切换agent")
        await chat.switch_agent(AgentType.TRANSLATOR)

        message = "请把'Hello World'翻译成中文"
        print(f"\n👤 用户: {message}")
        print(f"🤖 翻译专家回复: ", end="")

        async for chunk in chat.process_message(message, auto_detect=False):
            print(chunk, end="", flush=True)
        print()
        
        # 测试3: 获取agent信息
        print("\n🧪 测试3: 获取agent信息")
        available_agents = await chat.get_available_agents()
        print(f"可用的agent类型: {available_agents}")
        
        for agent_type in AgentType:
            info = await chat.get_agent_info(agent_type)
            print(f"\n{agent_type.value} agent:")
            print(f"  名称: {info['name']}")
            print(f"  工具: {info['tools']}")
            print(f"  描述: {info['description']}")
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        await chat.close()

async def main():
    """主测试函数"""
    print("🚀 开始Agent系统测试...")
    await test_agent_chat()
    print("\n✅ Agent系统测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
