#!/usr/bin/env python3
"""
工具系统测试
"""

import asyncio
from tools import tools_manager, ToolCategory, ToolPermission, BaseTool

class TestTool(BaseTool):
    """测试工具"""
    
    def __init__(self):
        super().__init__(
            name="test_tool",
            description="这是一个测试工具",
            category=ToolCategory.CUSTOM
        )
    
    async def execute(self, message: str = "Hello") -> str:
        return f"测试工具收到消息: {message}"

async def test_tools_manager():
    """测试工具管理器"""
    print("🧪 开始测试工具管理器...")
    
    # 测试1: 查看默认工具
    print("\n📋 默认工具列表:")
    tools_info = tools_manager.get_tools_info()
    print(f"总工具数: {tools_info['total_tools']}")
    print(f"分类统计: {tools_info['categories']}")
    print(f"权限统计: {tools_info['permissions']}")
    
    # 测试2: 注册自定义工具
    print("\n🔧 注册自定义工具...")
    test_tool = TestTool()
    tools_manager.register_tool(test_tool)
    
    # 测试3: 按分类获取工具
    print("\n📂 按分类获取工具:")
    for category in ToolCategory:
        tools = tools_manager.get_tools_by_category(category)
        if tools:
            print(f"{category.value}: {[tool.name for tool in tools]}")
    
    # 测试4: 测试工具执行
    print("\n⚡ 测试工具执行:")
    
    # 测试天气工具
    weather_tool = tools_manager.get_tool("get_weather")
    if weather_tool:
        result = await weather_tool("北京")
        print(f"天气工具: {result}")
    
    # 测试计算工具
    calc_tool = tools_manager.get_tool("calculate")
    if calc_tool:
        result = await calc_tool("2 + 3 * 4")
        print(f"计算工具: {result}")
    
    # 测试自定义工具
    custom_tool = tools_manager.get_tool("test_tool")
    if custom_tool:
        result = await custom_tool("测试消息")
        print(f"自定义工具: {result}")
    
    # 测试5: 工具使用统计
    print("\n📊 工具使用统计:")
    stats = tools_manager.get_usage_stats()
    print(f"总使用次数: {stats['total_usage']}")
    print(f"最常用工具: {stats['most_used'][:3]}")

async def main():
    """主测试函数"""
    print("🚀 开始工具系统测试...")
    await test_tools_manager()
    print("\n✅ 工具系统测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
