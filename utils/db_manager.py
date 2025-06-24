#!/usr/bin/env python3
"""
MySQL数据库管理工具
用于查看、管理会话数据
"""

import asyncio
import sys
from database import ConversationDatabase, DB_CONFIG

async def show_all_conversations():
    """显示所有会话"""
    db = ConversationDatabase(**DB_CONFIG)
    await db.init_database()
    
    conversations = await db.get_all_conversations()
    
    if not conversations:
        print("📭 没有找到任何会话")
        return
    
    print(f"📋 找到 {len(conversations)} 个会话:")
    print("-" * 80)
    
    for conv_id in conversations:
        summary = await db.get_conversation_summary(conv_id)
        print(f"🗨️  会话ID: {conv_id}")
        print(f"   📊 消息总数: {summary['total_messages']}")
        print(f"   🕐 首次消息: {summary['first_message_time']}")
        print(f"   🕑 最后消息: {summary['last_message_time']}")
        print("-" * 40)
    
    await db.close_connection_pool()

async def show_conversation_detail(conversation_id: str):
    """显示指定会话的详细内容"""
    db = ConversationDatabase(**DB_CONFIG)
    await db.init_database()
    
    messages = await db.get_recent_messages(conversation_id, limit=100)
    
    if not messages:
        print(f"📭 会话 {conversation_id} 没有找到任何消息")
        await db.close_connection_pool()
        return
    
    print(f"💬 会话 {conversation_id} 的消息记录:")
    print("=" * 80)
    
    for i, msg in enumerate(messages, 1):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        print(f"{i}. {role_icon} {msg['role'].upper()} [{msg['timestamp']}]")
        print(f"   {msg['content']}")
        print("-" * 40)
    
    await db.close_connection_pool()

async def delete_conversation_interactive():
    """交互式删除会话"""
    db = ConversationDatabase(**DB_CONFIG)
    await db.init_database()
    
    conversations = await db.get_all_conversations()
    
    if not conversations:
        print("📭 没有找到任何会话")
        await db.close_connection_pool()
        return
    
    print("🗑️  选择要删除的会话:")
    for i, conv_id in enumerate(conversations, 1):
        summary = await db.get_conversation_summary(conv_id)
        print(f"{i}. {conv_id} ({summary['total_messages']} 条消息)")
    
    try:
        choice = int(input("\n请输入序号 (0 取消): "))
        if choice == 0:
            print("❌ 取消删除")
            await db.close_connection_pool()
            return
        
        if 1 <= choice <= len(conversations):
            conv_id = conversations[choice - 1]
            confirm = input(f"确认删除会话 '{conv_id}' 吗? (y/N): ")
            
            if confirm.lower() == 'y':
                await db.delete_conversation(conv_id)
                print(f"✅ 会话 '{conv_id}' 已删除")
            else:
                print("❌ 取消删除")
        else:
            print("❌ 无效的选择")
            
    except ValueError:
        print("❌ 请输入有效的数字")
    
    await db.close_connection_pool()

async def test_connection():
    """测试数据库连接"""
    print("🔌 测试MySQL数据库连接...")
    print(f"配置信息:")
    print(f"  主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  数据库: {DB_CONFIG['database']}")
    print(f"  用户: {DB_CONFIG['user']}")
    
    try:
        db = ConversationDatabase(**DB_CONFIG)
        await db.init_database()
        
        async with db.get_connection() as cursor:
            await cursor.execute("SELECT VERSION()")
            version = await cursor.fetchone()
            print(f"✅ 连接成功！MySQL版本: {version[0]}")
            
            await cursor.execute("SELECT COUNT(*) FROM conversations")
            count = await cursor.fetchone()
            print(f"📊 当前数据库中有 {count[0]} 条消息")
        
        await db.close_connection_pool()
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 请检查:")
        print("  1. MySQL服务器是否正在运行")
        print("  2. 连接配置是否正确")
        print("  3. 用户权限是否足够")

def print_help():
    """显示帮助信息"""
    print("""
🛠️  MySQL数据库管理工具

用法: python utils/db_manager.py [命令] [参数]

命令:
  list                    - 显示所有会话
  show <conversation_id>  - 显示指定会话的详细内容
  delete                  - 交互式删除会话
  test                    - 测试数据库连接
  help                    - 显示此帮助信息

示例:
  python utils/db_manager.py list
  python utils/db_manager.py show user123
  python utils/db_manager.py test

环境变量配置:
  MYSQL_HOST=localhost
  MYSQL_PORT=3306
  MYSQL_USER=root
  MYSQL_PASSWORD=your_password
  MYSQL_DATABASE=ai_assistant
    """)

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        await show_all_conversations()
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ 请提供会话ID")
            return
        await show_conversation_detail(sys.argv[2])
    
    elif command == "delete":
        await delete_conversation_interactive()
    
    elif command == "test":
        await test_connection()
    
    elif command == "help":
        print_help()
    
    else:
        print(f"❌ 未知命令: {command}")
        print_help()

if __name__ == "__main__":
    asyncio.run(main())
