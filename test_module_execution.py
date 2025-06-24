#!/usr/bin/env python3
"""
验证模块级代码的自动执行
"""

# 创建一个测试模块文件
test_module_content = '''
print("🎯 模块开始加载...")

# 这是类定义
class TestClass:
    def __init__(self):
        print("  📦 TestClass 实例被创建")

# 这是函数定义
def test_function():
    print("  🔧 test_function 被调用")
    return "函数执行完成"

# 这是模块级变量
module_variable = "我是模块级变量"
print(f"  📝 模块级变量创建: {module_variable}")

# 这是模块级函数调用 - 会自动执行！
result = test_function()
print(f"  ✅ 模块级函数调用结果: {result}")

# 这是模块级类实例化 - 也会自动执行！
instance = TestClass()

print("🎉 模块加载完成！")
'''

# 写入测试模块
with open('test_auto_execution.py', 'w', encoding='utf-8') as f:
    f.write(test_module_content)

print("📁 创建了测试模块 test_auto_execution.py")
print("🔍 现在导入这个模块，观察自动执行...")
print("-" * 50)

# 导入模块 - 观察自动执行
import test_auto_execution

print("-" * 50)
print("✅ 导入完成！")

# 验证模块内容已经执行
print(f"📝 访问模块变量: {test_auto_execution.module_variable}")
print(f"📦 访问模块实例: {test_auto_execution.instance}")

# 清理
import os
os.remove('test_auto_execution.py')
print("🗑️ 清理测试文件")
