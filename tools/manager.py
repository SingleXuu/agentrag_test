"""
工具管理器
"""

from typing import Dict, List, Optional, Set, Callable
from .base import BaseTool, ToolCategory, ToolPermission

class ToolsManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        self.permissions: Dict[ToolPermission, Set[str]] = {
            ToolPermission.PUBLIC: set(),
            ToolPermission.RESTRICTED: set(),
            ToolPermission.ADMIN: set()
        }
    
    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
        
        # 按分类组织
        if tool.category not in self.categories:
            self.categories[tool.category] = []
        self.categories[tool.category].append(tool.name)
        
        # 按权限组织
        self.permissions[tool.permission].add(tool.name)
        
        print(f"✅ 注册工具: {tool.name} ({tool.category.value})")
    
    def unregister_tool(self, tool_name: str):
        """注销工具"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            
            # 从分类中移除
            if tool.category in self.categories:
                self.categories[tool.category].remove(tool_name)
            
            # 从权限中移除
            self.permissions[tool.permission].discard(tool_name)
            
            # 删除工具
            del self.tools[tool_name]
            print(f"🗑️ 注销工具: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tools.get(tool_name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """按分类获取工具"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names]
    
    def get_tools_by_permission(self, permission: ToolPermission) -> List[BaseTool]:
        """按权限获取工具"""
        tool_names = self.permissions.get(permission, set())
        return [self.tools[name] for name in tool_names]
    
    def get_available_tools(self, 
                          categories: Optional[List[ToolCategory]] = None,
                          permissions: Optional[List[ToolPermission]] = None) -> List[BaseTool]:
        """获取可用工具列表"""
        available_tools = []
        
        for tool in self.tools.values():
            # 检查分类过滤
            if categories and tool.category not in categories:
                continue
            
            # 检查权限过滤
            if permissions and tool.permission not in permissions:
                continue
            
            available_tools.append(tool)
        
        return available_tools
    
    def get_tool_functions(self, tool_names: List[str]) -> List[Callable]:
        """获取工具函数列表（用于AutoGen）"""
        import inspect
        functions = []

        for name in tool_names:
            if name in self.tools:
                tool = self.tools[name]

                # 获取原始execute方法的签名
                original_sig = inspect.signature(tool.execute)

                # 创建一个包装函数，保持原始签名
                def create_wrapper(tool_instance, sig):
                    # 动态创建函数参数
                    params = []
                    for param_name, param in sig.parameters.items():
                        if param_name not in ['self', 'args', 'kwargs']:
                            params.append(param.replace(annotation=str))

                    # 创建新的签名
                    new_sig = sig.replace(parameters=params)

                    async def wrapper(*args, **kwargs):
                        try:
                            return await tool_instance.execute(*args, **kwargs)
                        except Exception as e:
                            print(f"❌ 工具 {tool_instance.name} 执行错误: {e}")
                            import traceback
                            traceback.print_exc()
                            return f"工具执行错误: {str(e)}"

                    # 设置函数签名
                    wrapper.__signature__ = new_sig
                    return wrapper

                wrapper = create_wrapper(tool, original_sig)

                # 设置函数属性
                wrapper.__name__ = tool.name
                wrapper.__doc__ = tool.description
                functions.append(wrapper)

        return functions
    
    def get_tools_info(self) -> Dict:
        """获取所有工具信息"""
        return {
            "total_tools": len(self.tools),
            "categories": {
                category.value: len(tools) 
                for category, tools in self.categories.items()
            },
            "permissions": {
                permission.value: len(tools)
                for permission, tools in self.permissions.items()
            },
            "tools": {
                name: {
                    "description": tool.description,
                    "category": tool.category.value,
                    "permission": tool.permission.value,
                    "usage_count": tool.usage_count,
                    "last_used": tool.last_used.isoformat() if tool.last_used else None
                }
                for name, tool in self.tools.items()
            }
        }
    
    def get_usage_stats(self) -> Dict:
        """获取工具使用统计"""
        stats = {
            "most_used": [],
            "least_used": [],
            "category_usage": {},
            "total_usage": 0
        }
        
        # 按使用次数排序
        sorted_tools = sorted(
            self.tools.items(), 
            key=lambda x: x[1].usage_count, 
            reverse=True
        )
        
        stats["most_used"] = [
            {"name": name, "count": tool.usage_count}
            for name, tool in sorted_tools[:5]
        ]
        
        stats["least_used"] = [
            {"name": name, "count": tool.usage_count}
            for name, tool in sorted_tools[-5:]
        ]
        
        # 按分类统计
        for category, tool_names in self.categories.items():
            category_usage = sum(
                self.tools[name].usage_count 
                for name in tool_names
            )
            stats["category_usage"][category.value] = category_usage
            stats["total_usage"] += category_usage
        
        return stats

# 全局工具管理器实例
tools_manager = ToolsManager()
