# 🤖 Multi-Agent AI Assistant

一个功能强大的多Agent AI助手系统，具备工具集成、记忆功能和MySQL数据库持久化。

## 📁 项目结构

```
ai-assistant/
├── agents/                 # Agent模块
│   ├── __init__.py
│   ├── types.py           # Agent类型定义
│   ├── config.py          # Agent配置
│   └── chat.py            # AgentChat主类
├── tools/                 # 工具系统
│   ├── __init__.py
│   ├── base.py            # 工具基类和枚举
│   ├── manager.py         # 工具管理器
│   ├── builtin.py         # 内置工具
│   └── custom.py          # 自定义工具
├── database/              # 数据库模块
│   ├── __init__.py
│   ├── config.py          # 数据库配置
│   └── mysql.py           # MySQL实现
├── app/                   # FastAPI应用
│   ├── __init__.py
│   ├── models.py          # API数据模型
│   └── main.py            # FastAPI主应用
├── tests/                 # 测试模块
│   ├── __init__.py
│   ├── test_tools.py      # 工具测试
│   └── test_agents.py     # Agent测试
├── utils/                 # 工具脚本
│   ├── __init__.py
│   └── db_manager.py      # 数据库管理工具
├── static/                # 静态文件
│   ├── style.css
│   └── script.js
├── main.py                # 主启动文件
├── index.html             # 前端页面
├── requirements.txt       # 依赖列表
└── README.md              # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置MySQL数据库

```sql
-- 创建数据库
CREATE DATABASE ai_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'ai_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ai_assistant.* TO 'ai_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 配置环境变量

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=ai_assistant
```

或者直接修改 `database/config.py` 文件。

### 4. 启动应用

```bash
python main.py
```

### 5. 访问应用

打开浏览器访问：http://localhost:8000

## 🤖 Agent类型

系统支持以下专业化Agent：

- **General** - 通用助手，支持所有功能
- **Weather** - 天气专家，专门处理天气查询
- **Calculator** - 计算专家，处理数学计算和单位转换
- **Search** - 搜索专家，专门处理信息搜索
- **Translator** - 翻译专家，处理多语言翻译
- **Coder** - 编程助手，处理代码分析和编程问题

## 🛠️ 工具系统

### 内置工具

- `get_weather` - 天气查询
- `calculate` - 数学计算
- `search_web` - 网络搜索
- `translate_text` - 文本翻译
- `analyze_code` - 代码分析
- `get_time` - 时间查询

### 自定义工具

- `generate_random` - 随机生成
- `convert_units` - 单位转换
- `manage_schedule` - 日程管理
- `query_database` - 数据库查询
- `send_email` - 邮件发送
- `file_operations` - 文件操作

## 📊 API端点

### 聊天相关
- `POST /chat` - 流式聊天
- `POST /chat/simple` - 简单聊天
- `GET /conversations/{id}/history` - 获取历史记录
- `DELETE /conversations/{id}` - 删除会话

### Agent管理
- `GET /agents` - 获取所有Agent
- `POST /agents/switch` - 切换Agent
- `GET /conversations/{id}/agent` - 获取当前Agent

### 工具管理
- `GET /tools` - 获取工具信息
- `GET /tools/categories` - 获取工具分类
- `GET /tools/category/{category}` - 按分类获取工具
- `GET /tools/stats` - 获取工具使用统计

### 系统信息
- `GET /health` - 健康检查
- `GET /stats` - 系统统计

## 🧪 测试

### 测试工具系统
```bash
python tests/test_tools.py
```

### 测试Agent系统
```bash
python tests/test_agents.py
```

## 🔧 管理工具

### 数据库管理
```bash
# 查看所有会话
python utils/db_manager.py list

# 查看特定会话
python utils/db_manager.py show user123

# 删除会话
python utils/db_manager.py delete

# 测试数据库连接
python utils/db_manager.py test
```

## 🎯 特性

### 🤖 多Agent架构
- 专业化Agent自动切换
- 每个Agent有专门的工具集
- 智能Agent检测

### 🛠️ 解耦工具系统
- 模块化工具设计
- 分类和权限管理
- 易于扩展新工具

### 💾 持久化记忆
- MySQL数据库存储
- 自动加载历史对话
- 会话管理功能

### ⚡ 流式响应
- 实时打字机效果
- Server-Sent Events
- 非阻塞处理

### 🌐 现代化前端
- 响应式设计
- 实时聊天界面
- Agent状态显示

## 🔧 扩展指南

### 添加新Agent类型

1. 在 `agents/types.py` 中添加新类型
2. 在 `agents/config.py` 中添加配置
3. 更新工具分类映射

### 添加新工具

1. 继承 `BaseTool` 类
2. 实现 `execute` 方法
3. 注册到工具管理器

```python
from tools import BaseTool, ToolCategory, register_custom_tool

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的自定义工具",
            category=ToolCategory.CUSTOM
        )
    
    async def execute(self, param: str) -> str:
        return f"处理: {param}"

# 注册工具
register_custom_tool(MyTool())
```

## 📝 配置说明

### 数据库配置
在 `database/config.py` 中修改数据库连接参数。

### Agent配置
在 `agents/config.py` 中修改Agent的系统消息和工具分配。

### 工具配置
在 `tools/` 目录下添加新的工具模块。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

🎉 享受使用多Agent AI助手的乐趣！
