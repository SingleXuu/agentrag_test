"""
内置工具集合
"""

from datetime import datetime
from .base import BaseTool, ToolCategory
from .manager import tools_manager

class WeatherTool(BaseTool):
    """天气查询工具"""
    
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="获取指定城市的天气信息",
            category=ToolCategory.WEATHER
        )
    
    async def execute(self, city: str) -> str:
        """获取天气信息"""
        # 这里可以集成真实的天气API
        weather_data = {
            "北京": "晴朗，25°C，微风",
            "上海": "多云，22°C，东南风",
            "广州": "小雨，28°C，南风",
            "深圳": "晴朗，30°C，无风"
        }
        
        result = weather_data.get(city, f"{city}的天气是73度，晴朗")
        return f"🌤️ {city}今天的天气：{result}"

class CalculatorTool(BaseTool):
    """计算器工具"""
    
    def __init__(self):
        super().__init__(
            name="calculate",
            description="执行数学计算",
            category=ToolCategory.CALCULATION
        )
    
    async def execute(self, expression: str) -> str:
        """执行数学计算"""
        try:
            # 安全的数学表达式计算
            allowed_chars = set('0123456789+-*/().,e ')
            if not all(c in allowed_chars for c in expression.replace(' ', '')):
                return "❌ 表达式包含不允许的字符"
            
            # 替换常见的数学符号
            safe_expr = expression.replace("^", "**").replace("×", "*").replace("÷", "/")
            result = eval(safe_expr)
            return f"📊 {expression} = {result}"
        except Exception as e:
            return f"❌ 计算错误: {str(e)}"

class SearchTool(BaseTool):
    """搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="search_web",
            description="搜索网络信息",
            category=ToolCategory.SEARCH
        )
    
    async def execute(self, query: str) -> str:
        """搜索网络信息"""
        # 这里可以集成真实的搜索API
        return f"🔍 搜索'{query}'的结果：\n• 相关信息1\n• 相关信息2\n• 相关信息3"

class TranslatorTool(BaseTool):
    """翻译工具"""
    
    def __init__(self):
        super().__init__(
            name="translate_text",
            description="翻译文本到指定语言",
            category=ToolCategory.TRANSLATION
        )
    
    async def execute(self, text: str, target_language: str = "英文") -> str:
        """翻译文本"""
        # 这里可以集成真实的翻译API
        translations = {
            "你好": {"英文": "Hello", "日文": "こんにちは", "法文": "Bonjour"},
            "谢谢": {"英文": "Thank you", "日文": "ありがとう", "法文": "Merci"},
            "再见": {"英文": "Goodbye", "日文": "さようなら", "法文": "Au revoir"}
        }
        
        if text in translations and target_language in translations[text]:
            result = translations[text][target_language]
        else:
            result = f"[{text}的{target_language}翻译]"
        
        return f"🌐 翻译结果：{text} → {result}"

class CodeAnalyzerTool(BaseTool):
    """代码分析工具"""
    
    def __init__(self):
        super().__init__(
            name="analyze_code",
            description="分析代码质量和提供建议",
            category=ToolCategory.CODE
        )
    
    async def execute(self, code: str, language: str = "python") -> str:
        """分析代码"""
        analysis = f"💻 {language.upper()}代码分析：\n"
        
        # 简单的代码分析逻辑
        if len(code.strip()) < 10:
            analysis += "• 代码过短，可能不完整\n"
        
        if "def " in code or "function " in code:
            analysis += "• ✅ 发现函数定义\n"
        
        if "#" in code or "//" in code or "/*" in code:
            analysis += "• ✅ 包含注释，良好的编程习惯\n"
        else:
            analysis += "• ⚠️ 建议添加注释\n"
        
        if "try" in code and "except" in code:
            analysis += "• ✅ 包含错误处理\n"
        else:
            analysis += "• ⚠️ 建议添加错误处理\n"
        
        return analysis

class TimeTool(BaseTool):
    """时间工具"""
    
    def __init__(self):
        super().__init__(
            name="get_time",
            description="获取当前时间信息",
            category=ToolCategory.TIME
        )
    
    async def execute(self, format_type: str = "datetime") -> str:
        """获取时间信息"""
        now = datetime.now()
        
        if format_type == "date":
            return f"📅 今天是：{now.strftime('%Y年%m月%d日')}"
        elif format_type == "time":
            return f"🕐 现在时间：{now.strftime('%H:%M:%S')}"
        else:
            return f"📅 当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"

def register_builtin_tools():
    """注册所有内置工具"""
    builtin_tools = [
        WeatherTool(),
        CalculatorTool(),
        SearchTool(),
        TranslatorTool(),
        CodeAnalyzerTool(),
        TimeTool()
    ]
    
    for tool in builtin_tools:
        tools_manager.register_tool(tool)
    
    print(f"✅ 已注册 {len(builtin_tools)} 个内置工具")

# 自动注册内置工具
register_builtin_tools()
