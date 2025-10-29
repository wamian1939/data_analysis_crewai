# CrewAI 数据分析系统

基于 CrewAI 框架的智能数据分析系统，通过多 Agent 协作实现自然语言到数据洞察的自动化流程。

## 项目概述

本系统通过三个 Agent 协作完成数据分析任务：

1. **DataEngineer** - 从数据库或 CSV 文件中提取数据
2. **BizAnalyst** - 分析数据并提取业务洞察
3. **Reporter** - 生成结构化的分析报告

### 核心功能

- **智能 NL2SQL**：自然语言问题转 SQL 查询
- **连续对话**：支持上下文记忆的多轮对话
- **多数据源**：支持 MySQL 数据库和 CSV 文件
- **Web 界面**：ChatGPT 风格的对话界面
- **RESTful API**：FastAPI 后端，支持前端和 BI 工具集成
- **Power BI 集成**：可直接作为 Power BI 数据源

### 技术栈

- CrewAI - 多 Agent 协作框架
- SQLAlchemy - 数据库 ORM
- FastAPI - API 框架
- OpenAI GPT - LLM 引擎
- Pandas - 数据处理

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 配置

创建 `config.py` 文件：

```python
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL_NAME = "gpt-4o-mini"

DB_CONFIG = {
    "user": "root",
    "password": "your_password",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "chinook",
}
```

### 启动

**一键启动（推荐）**

```bash
start_all.bat
```

**分别启动**

```bash
# API 服务
start_api.bat

# Web 前端
start_web.bat
```

访问 http://localhost:8080 即可使用。

## 使用方式

### Web 界面

1. 打开 http://localhost:8080
2. 输入自然语言问题
3. 查看分析结果和数据

**示例问题：**

- 哪个国家的客户消费最多？
- 收入最高的艺人 TOP 10？
- 最受欢迎的音乐流派是什么？

### 命令行

```bash
python ask_agent.py "哪个国家的客户消费最多？"
```

### API 调用

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"question": "哪个国家的客户消费最多？"}
)

result = response.json()
```

## Power BI 集成

### 生成数据

```bash
python generate_powerbi_data.py
```

### 连接步骤

1. 打开 Power BI Desktop
2. 获取数据 → Web
3. 输入：`http://localhost:8000/api/v1/history`
4. 加载数据

## 连续对话

系统支持多轮对话，AI 会记住最近 3 轮对话内容：

```
用户: 哪个国家的客户消费最多？
AI: USA 客户消费最高...

用户: 它的平均客单价是多少？
AI: USA 的平均客单价是 $5.7...
```

**快捷键：**

- `Enter` - 发送消息
- `Ctrl+N` - 新对话

## API 接口

### 数据分析

```
POST /api/v1/analyze
```

请求体：

```json
{
  "question": "哪个国家的客户消费最多？",
  "user_id": "user_001",
  "conversation_history": []
}
```

### 查询历史

```
GET /api/v1/history?limit=50
```

### 健康检查

```
GET /health
```

详细文档：http://localhost:8000/docs

## 项目结构

```
data_analysis/
├── api/                  # FastAPI 后端
├── web/                  # Web 前端
├── agents/               # Agent 定义
├── tools/                # 工具层
├── crew.py               # Agent 编排
├── main.py               # CLI 入口
└── config.py             # 配置文件
```

## 配置说明

### 环境变量

可以使用 `.env` 文件替代 `config.py`：

```env
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=gpt-4o-mini

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chinook
```

### 数据库

本项目使用 Chinook 示例数据库：

```bash
# 下载 SQL 文件
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_MySql.sql

# 导入数据库
mysql -u root -p < Chinook_MySql.sql
```

## 常见问题

**Q: API 启动失败？**

检查 MySQL 是否运行，`config.py` 配置是否正确。

**Q: Web 界面一直加载？**

CrewAI 分析需要 30-60 秒，请耐心等待。按 F12 查看控制台确认是否有错误。

**Q: 如何切换数据库？**

修改 `config.py` 中的 `DB_CONFIG`，系统会自动读取新数据库的 schema。

**Q: Power BI 没有数据？**

先运行 `python generate_powerbi_data.py` 生成示例数据。

## 开发说明

### 添加新 Agent

在 `agents/` 目录创建新的 Agent 文件，然后在 `crew.py` 中注册。

### 添加新工具

在 `tools/` 目录创建新的工具函数，使用 `@tool` 装饰器。

### 修改 Prompt

编辑 `crew.py` 中的任务描述或 `agents/` 中的 Agent backstory。

## 依赖包

核心依赖：

```
crewai>=0.90.0
fastapi>=0.104.0
sqlalchemy>=2.0.0
openai>=1.0.0
pandas>=2.0.0
```

完整依赖见 `requirements.txt`。

## 安全提示

- 不要提交 `config.py` 到 Git（已在 `.gitignore` 中）
- 生产环境建议使用环境变量管理密钥
- API 当前无认证，生产环境需添加身份验证

## 许可证

MIT License

## 作者

GitHub: [wamian1939](https://github.com/wamian1939/data_analysis_crewai)
