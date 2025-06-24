"""
数据库配置
"""

import os

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "damon123"),
    "database": os.getenv("MYSQL_DATABASE", "ai_assistant")
}
