# 🤖 CrewAI 数据分析系统

基于 CrewAI 框架的智能数据分析系统，通过多 Agent 协作完成从自然语言到 SQL 查询、数据提取、洞察分析和报告生成的全流程。

## 📋 项目概述

### 核心思路

**自然语言 → 智能查询（SQL/CSV）→ 数据提取 → KPI/洞察 → Markdown 报告**

通过三个智能 Agent 顺序协作完成数据分析任务：

1. **DataEngineer（数据工程师）**：

   - 🤖 使用 LLM 动态生成 SQL
   - 📊 支持多数据源：MySQL + CSV
   - 🧠 智能判断使用哪个数据源

2. **BizAnalyst（业务分析师）**：从数据中提取关键业务洞察

3. **Reporter（报告撰写员）**：生成结构化的管理层报告

### 🎯 核心特性

#### ✨ 智能 NL2SQL

- **理解任意问题**：不局限于预设模板
- **动态生成 SQL**：根据数据库 schema 自动生成查询
- **自然语言对话**：像和人对话一样提问

#### 💬 连续对话（v3.1 新增）

- **上下文记忆**：AI 记住最近 3 轮对话
- **智能追问**：支持代词引用和深入分析
- **会话管理**：自动保存，快捷键支持（Ctrl+N）
- **详见**：[连续对话使用说明](连续对话使用说明.md)

#### 📁 多数据源支持

- **MySQL 数据库**：Chinook 音乐商店数据（示例）
- **CSV 文件**：支持本地 CSV 文件分析
- **自动识别**：Agent 自动选择合适的数据源

#### 🌐 RESTful API

- **FastAPI 后端**：高性能异步 API 服务
- **问答接口**：向智能体提问
- **Power BI 集成**：直接连接到 Power BI 进行可视化

### 技术栈

- **CrewAI**: 多 Agent 协作框架
- **SQLAlchemy**: 数据库连接与查询
- **MySQL**: 数据存储（Chinook 示例数据库）
- **OpenAI GPT**: Agent 决策引擎
- **FastAPI**: API 服务框架
- **Pandas**: 数据处理

## 🏗️ 项目结构

```
data_analysis/
├── main.py                 # CLI 模式入口
├── crew.py                 # Agent 编排
├── config.py               # 配置文件
├── requirements.txt        # 依赖包
│
├── web/                    # Web 前端（精简版）
│   ├── index.html         # 主页（问答界面）
│   ├── history.html       # 历史记录页面
│   ├── style.css          # 全局样式
│   ├── app.js             # 主页逻辑
│   └── history.js         # 历史页面逻辑
│
├── api/                    # API 服务（精简版）
│   ├── main.py            # API 入口
│   ├── models.py          # 数据模型
│   └── services.py        # 业务逻辑
│
├── agents/                 # Agent 定义
│   ├── data_engineer.py
│   ├── biz_analyst.py
│   └── reporter.py
│
├── tools/                  # 工具层
│   ├── sql_tool.py        # SQL 工具
│   ├── nl2sql.py          # NL2SQL
│   ├── schema_reader.py   # Schema 读取
│   ├── insight.py         # 洞察提取
│   └── csv_tool.py        # CSV 工具
│
└── report/output/          # 报告输出
```

## 🚀 快速开始

### 1. 环境准备

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

创建 `config.py` 文件：

```python
# OpenAI API 配置
OPENAI_API_KEY = "sk-your-openai-api-key"
OPENAI_MODEL_NAME = "gpt-4o-mini"

# MySQL 数据库配置
DB_CONFIG = {
    "user": "root",
    "password": "your_password",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "chinook",
}
```

### 2. 准备数据库

本项目使用 Chinook 示例数据库（音乐商店数据）。

```bash
# 下载 Chinook MySQL 脚本
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_MySql.sql

# 导入数据库
mysql -u root -p < Chinook_MySql.sql
```

### 3. 启动 API 服务

#### Windows

```bash
start_api.bat
```

#### Linux/Mac

```bash
bash start_api.sh
```

#### 手动启动

```bash
python api/main.py
```

服务启动后访问：

- **API 文档（Swagger）**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 4. 启动 Web 前端（推荐）

#### Windows

```bash
start_web.bat
```

#### Linux/Mac

```bash
bash start_web.sh
```

在浏览器中访问：**http://localhost:8080**

## 💬 向智能体提问

### 方法 1: Web 界面（推荐）

1. 访问 **http://localhost:8080**
2. 在输入框中输入问题
3. 点击「🚀 开始分析」按钮
4. 查看分析结果和业务洞察

**特性**：

- ✨ 简约美观的界面
- 📊 可视化结果展示
- 📈 查询历史记录
- 💡 示例问题快速选择

### 方法 2: 命令行

```bash
python ask_agent.py "哪个国家的客户消费最多？"
```

### 方法 3: Python 代码

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"question": "哪个国家的客户消费最多？"}
)

result = response.json()
print(result['report'])
```

### 方法 4: cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"question": "哪个国家的客户消费最多？"}'
```

## 📊 Power BI 连接

### 1. 生成示例数据

```bash
python generate_powerbi_data.py
```

### 2. 在 Power BI 中连接

1. 打开 Power BI Desktop
2. **获取数据** → **Web**
3. 输入 URL：`http://localhost:8000/api/v1/history`
4. 点击「确定」即可加载数据

### 3. 可用字段

- `query_id`: 查询 ID
- `question`: 用户问题
- `status`: 查询状态
- `executed_sql`: 执行的 SQL
- `result_rows`: 结果行数
- `execution_time`: 执行时间
- `created_at`: 创建时间

### 4. 自动刷新

在 Power BI 中设置数据源为「自动刷新」，即可实时同步最新的分析数据。

## 🎯 支持的问题类型

### 聚合查询

```
"销售总额是多少？"
"平均每张发票金额？"
"客户总数是多少？"
```

### TOP N 查询

```
"哪个国家的客户消费最多？"
"收入最高的艺人 TOP 10？"
"最畅销的专辑排名？"
```

### 趋势分析

```
"按月份汇总的销售趋势？"
"不同流派的销售对比？"
"客户地理分布？"
```

### CSV 数据分析

```
"分析 data/sales.csv 的销售情况"
"data/customers.csv 中客户年龄分布"
```

## 🔌 API 接口文档

### 1. 数据分析

**POST** `/api/v1/analyze`

请求示例：

```json
{
  "question": "哪个国家的客户消费最多？",
  "user_id": "user_001",
  "save_result": true
}
```

响应示例：

```json
{
  "query_id": "q_20250129_143052_a1b2c3",
  "question": "哪个国家的客户消费最多？",
  "status": "success",
  "data": [...],
  "insights": ["USA 客户消费最多，占比 22%"],
  "report": "# 分析报告\n\n...",
  "executed_sql": "SELECT...",
  "execution_time": 5.23
}
```

### 2. 查询历史（Power BI 数据源）

**GET** `/api/v1/history?limit=100`

参数：

- `limit`: 返回数量（默认 50）
- `skip`: 偏移量（用于分页）
- `user_id`: 用户 ID（可选）

### 3. 健康检查

**GET** `/health`

## 📦 依赖说明

```txt
crewai>=0.90.0              # 多 Agent 框架
crewai-tools>=0.20.0        # 工具集
sqlalchemy>=2.0.0           # 数据库 ORM
mysql-connector-python      # MySQL 连接器
pandas>=2.0.0               # 数据处理
openai>=1.0.0               # OpenAI API
fastapi>=0.104.0            # API 框架
uvicorn[standard]           # ASGI 服务器
```

## 🔒 安全提示

1. **不要将 `config.py` 提交到 Git**，已在 `.gitignore` 中排除
2. **生产环境**请使用环境变量管理密钥
3. **API 访问**建议添加身份验证（当前为演示版本）

## 🎓 简历项目描述

### 智能数据分析系统（基于 CrewAI 多 Agent 框架）

- **项目背景**：构建基于多 Agent 协作的智能数据分析系统，实现自然语言到数据洞察的端到端流程
- **核心技术**：
  - 基于 **CrewAI** 框架实现多 Agent 协作（DataEngineer、BizAnalyst、Reporter）
  - 使用 **OpenAI GPT** + Few-shot Learning 实现 NL2SQL，将自然语言问题转换为 SQL 查询
  - 通过 **SQLAlchemy** 实现动态 Schema 读取，支持跨数据库切换（MySQL/PostgreSQL）
  - 设计 **FastAPI** RESTful API 服务，支持前端调用和 BI 工具集成
- **系统架构**：
  - **数据工程层**：动态 SQL 生成、多数据源支持（MySQL + CSV）、查询安全控制
  - **业务分析层**：KPI 提取、趋势分析、洞察生成
  - **报告层**：Markdown 格式报告、API 接口输出
- **BI 集成**：实现 Power BI 数据源连接，支持实时刷新和历史数据可视化

- **成果**：
  - 支持 **任意自然语言问题**，无需预定义模板
  - **零代码切换数据库**，自动读取 Schema
  - **API 化部署**，可对接 Web 前端和 BI 工具
  - 完整的查询历史记录和结果可追溯

## 📄 许可证

MIT License

## 👨‍💻 作者

- GitHub: [YourUsername]
- 项目链接: [Repository URL]

---

**⭐ 如果觉得有帮助，请给个 Star！**
