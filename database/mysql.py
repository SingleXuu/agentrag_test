"""
MySQL数据库实现
"""

import aiomysql
from datetime import datetime
from typing import List, Dict
from contextlib import asynccontextmanager

class ConversationDatabase:
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 3306,
                 user: str = "root",
                 password: str = "",
                 database: str = "ai_assistant"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool = None
    
    async def init_connection_pool(self):
        """初始化数据库连接池"""
        try:
            # 首先连接到MySQL服务器（不指定数据库）
            temp_pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                autocommit=True
            )
            
            # 创建数据库（如果不存在）
            async with temp_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            temp_pool.close()
            await temp_pool.wait_closed()
            
            # 创建连接到指定数据库的连接池
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                charset='utf8mb4',
                autocommit=True,
                minsize=5,
                maxsize=20
            )
            print("✅ MySQL连接池初始化完成")
        except Exception as e:
            print(f"❌ MySQL连接池初始化失败: {e}")
            raise
    
    async def close_connection_pool(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("✅ MySQL连接池已关闭")
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接的上下文管理器"""
        if not self.pool:
            await self.init_connection_pool()
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                yield cursor
    
    async def init_database(self):
        """初始化数据库表"""
        async with self.get_connection() as cursor:
            # 创建会话表
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id VARCHAR(255) NOT NULL,
                    role ENUM('user', 'assistant') NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_index INT NOT NULL,
                    INDEX idx_conversation_id (conversation_id),
                    INDEX idx_conversation_timestamp (conversation_id, timestamp),
                    INDEX idx_message_index (conversation_id, message_index)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            print("✅ MySQL数据库和表初始化完成")
    
    async def save_message(self, conversation_id: str, role: str, content: str):
        """保存单条消息到数据库"""
        async with self.get_connection() as cursor:
            # 获取当前会话的最大消息序号
            await cursor.execute("""
                SELECT COALESCE(MAX(message_index), 0) 
                FROM conversations 
                WHERE conversation_id = %s
            """, (conversation_id,))
            
            result = await cursor.fetchone()
            max_index = result[0] if result else 0
            new_index = max_index + 1
            
            # 插入新消息
            await cursor.execute("""
                INSERT INTO conversations (conversation_id, role, content, message_index)
                VALUES (%s, %s, %s, %s)
            """, (conversation_id, role, content, new_index))
            
            print(f"💾 保存消息: {conversation_id} - {role} - 序号{new_index}")
    
    async def get_recent_messages(self, conversation_id: str, limit: int = 20) -> List[Dict]:
        """获取指定会话的最近N条消息"""
        async with self.get_connection() as cursor:
            await cursor.execute("""
                SELECT role, content, timestamp, message_index
                FROM conversations 
                WHERE conversation_id = %s
                ORDER BY message_index DESC
                LIMIT %s
            """, (conversation_id, limit))
            
            rows = await cursor.fetchall()
            
            # 转换为字典格式并按时间正序排列
            messages = []
            for row in reversed(rows):  # 反转以获得正确的时间顺序
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None,
                    "message_index": row[3]
                })
            
            print(f"📖 读取会话 {conversation_id} 的 {len(messages)} 条历史消息")
            return messages
    
    async def get_conversation_summary(self, conversation_id: str) -> Dict:
        """获取会话摘要信息"""
        async with self.get_connection() as cursor:
            await cursor.execute("""
                SELECT 
                    COUNT(*) as total_messages,
                    MIN(timestamp) as first_message_time,
                    MAX(timestamp) as last_message_time
                FROM conversations 
                WHERE conversation_id = %s
            """, (conversation_id,))
            
            row = await cursor.fetchone()
            
            return {
                "conversation_id": conversation_id,
                "total_messages": row[0] if row else 0,
                "first_message_time": row[1].strftime('%Y-%m-%d %H:%M:%S') if row and row[1] else None,
                "last_message_time": row[2].strftime('%Y-%m-%d %H:%M:%S') if row and row[2] else None
            }
    
    async def get_all_conversations(self) -> List[str]:
        """获取所有会话ID列表"""
        async with self.get_connection() as cursor:
            await cursor.execute("""
                SELECT DISTINCT conversation_id 
                FROM conversations 
                GROUP BY conversation_id
                ORDER BY MAX(timestamp) DESC
            """)
            
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def delete_conversation(self, conversation_id: str):
        """删除指定会话的所有消息"""
        async with self.get_connection() as cursor:
            await cursor.execute("""
                DELETE FROM conversations 
                WHERE conversation_id = %s
            """, (conversation_id,))
            
            print(f"🗑️ 已删除会话 {conversation_id} 的所有消息")
    
    async def cleanup_old_messages(self, days: int = 30):
        """清理超过指定天数的旧消息"""
        async with self.get_connection() as cursor:
            await cursor.execute("""
                DELETE FROM conversations 
                WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
            """, (days,))
            
            print(f"🧹 已清理超过 {days} 天的旧消息")
