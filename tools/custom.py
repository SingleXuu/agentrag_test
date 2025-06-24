"""
自定义工具集合
"""

import json
import random
from datetime import datetime
from .base import BaseTool, ToolCategory, ToolPermission
from .manager import tools_manager

class RandomTool(BaseTool):
    """随机数生成工具"""
    
    def __init__(self):
        super().__init__(
            name="generate_random",
            description="生成随机数或随机选择",
            category=ToolCategory.CUSTOM
        )
    
    async def execute(self, type: str = "number", min_val: int = 1, max_val: int = 100) -> str:
        """生成随机内容"""
        if type == "number":
            result = random.randint(min_val, max_val)
            return f"🎲 随机数：{result} (范围：{min_val}-{max_val})"
        
        elif type == "choice":
            choices = ["选项A", "选项B", "选项C", "选项D"]
            result = random.choice(choices)
            return f"🎯 随机选择：{result}"
        
        elif type == "password":
            import string
            chars = string.ascii_letters + string.digits
            password = ''.join(random.choice(chars) for _ in range(12))
            return f"🔐 随机密码：{password}"
        
        else:
            return f"❌ 不支持的随机类型：{type}"

class UnitConverterTool(BaseTool):
    """单位转换工具"""
    
    def __init__(self):
        super().__init__(
            name="convert_units",
            description="单位转换",
            category=ToolCategory.CALCULATION
        )
    
    async def execute(self, value: float, from_unit: str, to_unit: str, unit_type: str = "length") -> str:
        """单位转换"""
        conversions = {
            "length": {
                "m": 1.0,
                "cm": 0.01,
                "mm": 0.001,
                "km": 1000.0,
                "inch": 0.0254,
                "ft": 0.3048
            },
            "weight": {
                "kg": 1.0,
                "g": 0.001,
                "lb": 0.453592,
                "oz": 0.0283495
            }
        }
        
        try:
            if unit_type in ["length", "weight"]:
                if from_unit in conversions[unit_type] and to_unit in conversions[unit_type]:
                    # 转换为基准单位，再转换为目标单位
                    base_value = value * conversions[unit_type][from_unit]
                    result = base_value / conversions[unit_type][to_unit]
                    return f"🔄 单位转换：{value} {from_unit} = {result:.4f} {to_unit}"
                else:
                    return f"❌ 不支持的单位：{from_unit} 或 {to_unit}"
            
            elif unit_type == "temperature":
                # 温度转换
                if from_unit == "celsius" and to_unit == "fahrenheit":
                    result = value * 9/5 + 32
                elif from_unit == "fahrenheit" and to_unit == "celsius":
                    result = (value - 32) * 5/9
                elif from_unit == "celsius" and to_unit == "kelvin":
                    result = value + 273.15
                elif from_unit == "kelvin" and to_unit == "celsius":
                    result = value - 273.15
                else:
                    return f"❌ 不支持的温度转换：{from_unit} 到 {to_unit}"
                
                return f"🌡️ 温度转换：{value}°{from_unit} = {result:.2f}°{to_unit}"
            
            else:
                return f"❌ 不支持的单位类型：{unit_type}"
                
        except Exception as e:
            return f"❌ 转换错误：{str(e)}"

class ScheduleTool(BaseTool):
    """日程管理工具"""
    
    def __init__(self):
        super().__init__(
            name="manage_schedule",
            description="管理日程安排",
            category=ToolCategory.CUSTOM
        )
        self.schedule = {}  # 简单的内存存储
    
    async def execute(self, action: str, date: str = "", event: str = "") -> str:
        """日程管理"""
        if action == "add":
            if date and event:
                if date not in self.schedule:
                    self.schedule[date] = []
                self.schedule[date].append(event)
                return f"📅 已添加日程：{date} - {event}"
            else:
                return "❌ 请提供日期和事件"
        
        elif action == "list":
            if date:
                events = self.schedule.get(date, [])
                if events:
                    return f"📅 {date} 的日程：\n" + "\n".join(f"• {e}" for e in events)
                else:
                    return f"📅 {date} 没有安排"
            else:
                if self.schedule:
                    result = "📅 所有日程：\n"
                    for d, events in self.schedule.items():
                        result += f"{d}:\n" + "\n".join(f"  • {e}" for e in events) + "\n"
                    return result
                else:
                    return "📅 暂无日程安排"
        
        elif action == "delete":
            if date in self.schedule:
                if event:
                    if event in self.schedule[date]:
                        self.schedule[date].remove(event)
                        return f"🗑️ 已删除日程：{date} - {event}"
                    else:
                        return f"❌ 未找到事件：{event}"
                else:
                    del self.schedule[date]
                    return f"🗑️ 已删除 {date} 的所有日程"
            else:
                return f"❌ 未找到日期：{date}"
        
        else:
            return f"❌ 不支持的操作：{action}"

class DatabaseTool(BaseTool):
    """数据库查询工具"""
    
    def __init__(self):
        super().__init__(
            name="query_database",
            description="查询数据库信息",
            category=ToolCategory.SYSTEM,
            permission=ToolPermission.RESTRICTED
        )
    
    async def execute(self, query: str, table: str = "users") -> str:
        """模拟数据库查询"""
        # 这里可以集成真实的数据库查询
        mock_data = {
            "users": [
                {"id": 1, "name": "张三", "age": 25},
                {"id": 2, "name": "李四", "age": 30},
                {"id": 3, "name": "王五", "age": 28}
            ],
            "orders": [
                {"id": 101, "user_id": 1, "amount": 299.99},
                {"id": 102, "user_id": 2, "amount": 199.50},
                {"id": 103, "user_id": 1, "amount": 89.00}
            ]
        }
        
        if table in mock_data:
            results = mock_data[table]
            return f"📊 查询表 '{table}' 结果：\n{json.dumps(results, ensure_ascii=False, indent=2)}"
        else:
            return f"❌ 表 '{table}' 不存在"

class EmailTool(BaseTool):
    """邮件发送工具"""
    
    def __init__(self):
        super().__init__(
            name="send_email",
            description="发送邮件",
            category=ToolCategory.SYSTEM,
            permission=ToolPermission.ADMIN
        )
    
    async def execute(self, to: str, subject: str, content: str) -> str:
        """模拟发送邮件"""
        # 这里可以集成真实的邮件发送服务
        return f"📧 邮件已发送：\n收件人：{to}\n主题：{subject}\n内容：{content[:50]}..."

class FileTool(BaseTool):
    """文件操作工具"""
    
    def __init__(self):
        super().__init__(
            name="file_operations",
            description="文件读写操作",
            category=ToolCategory.SYSTEM,
            permission=ToolPermission.RESTRICTED
        )
    
    async def execute(self, operation: str, filename: str, content: str = "") -> str:
        """文件操作"""
        try:
            if operation == "read":
                # 模拟读取文件
                return f"📄 读取文件 '{filename}'：\n[文件内容模拟]"
            
            elif operation == "write":
                # 模拟写入文件
                return f"✍️ 已写入文件 '{filename}'：\n内容长度：{len(content)} 字符"
            
            elif operation == "list":
                # 模拟列出文件
                mock_files = ["document.txt", "image.jpg", "data.json", "script.py"]
                return f"📁 目录文件列表：\n" + "\n".join(f"• {f}" for f in mock_files)
            
            else:
                return f"❌ 不支持的操作：{operation}"
                
        except Exception as e:
            return f"❌ 文件操作错误：{str(e)}"

class APITool(BaseTool):
    """API调用工具"""
    
    def __init__(self):
        super().__init__(
            name="call_api",
            description="调用外部API",
            category=ToolCategory.CUSTOM,
            permission=ToolPermission.RESTRICTED
        )
    
    async def execute(self, url: str, method: str = "GET", data: str = "") -> str:
        """模拟API调用"""
        # 这里可以集成真实的HTTP客户端
        mock_responses = {
            "https://api.github.com/users/octocat": {
                "login": "octocat",
                "name": "The Octocat",
                "public_repos": 8
            },
            "https://jsonplaceholder.typicode.com/posts/1": {
                "userId": 1,
                "id": 1,
                "title": "sunt aut facere repellat",
                "body": "quia et suscipit..."
            }
        }
        
        if url in mock_responses:
            response = mock_responses[url]
            return f"🌐 API调用成功：\n{json.dumps(response, ensure_ascii=False, indent=2)}"
        else:
            return f"🌐 API调用 {method} {url}：\n[模拟响应数据]"

def register_custom_tools():
    """注册所有自定义工具"""
    custom_tools = [
        RandomTool(),
        UnitConverterTool(),
        ScheduleTool(),
        DatabaseTool(),
        EmailTool(),
        FileTool(),
        APITool()
    ]
    
    for tool in custom_tools:
        tools_manager.register_tool(tool)
    
    print(f"✅ 已注册 {len(custom_tools)} 个自定义工具")

# 自动注册自定义工具
register_custom_tools()
