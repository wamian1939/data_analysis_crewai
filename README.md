# 🤖 CrewAI 数据分析系统

基于 CrewAI 框架的智能数据分析系统，通过多 Agent 协作完成从自然语言到 SQL 查询、数据提取、洞察分析和报告生成的全流程。

## 📋 项目概述

### 核心思路

**自然语言 → 智能查询（SQL/CSV）→ 数据提取 → KPI/洞察 → Markdown 报告**

通过三个智能 Agent 顺序协作完成数据分析任务：

1. **DataEngineer（数据工程师）**：

   - 🤖 **使用 LLM 动态生成 SQL**（不再依赖固定模板）
   - 📊 **支持多数据源**：MySQL 数据库 + CSV 文件
   - 🧠 智能判断使用哪个数据源

2. **BizAnalyst（业务分析师）**：从数据中提取关键业务洞察

3. **Reporter（报告撰写员）**：生成结构化的管理层报告

### 🎯 核心特性（v2.0 新增）

#### ✨ LLM 驱动的智能 NL2SQL

- **理解任意问题**：不再局限于预设模板
- **动态生成 SQL**：根据数据库 schema 自动生成查询
- **自然语言对话**：像和人对话一样提问

#### 📁 多数据源支持

- **MySQL 数据库**：Chinook 音乐商店数据（示例）
- **CSV 文件**：支持本地 CSV 文件分析
- **自动识别**：Agent 自动选择合适的数据源

### 技术栈

- **CrewAI**: 多 Agent 协作框架
- **SQLAlchemy**: 数据库连接与查询
- **MySQL**: 数据存储（Chinook 示例数据库）
- **OpenAI GPT**: Agent 决策引擎
- **Pandas**: 数据处理
- **Markdown**: 报告格式

## 🏗️ 项目结构

```
data_analysis/
├── crew.py                 # Agent 编排和任务定义
├── main.py                 # 程序入口
├── requirements.txt        # 依赖包
├── README.md              # 项目文档
├── .env                   # 环境配置（需创建）
│
├── agents/                # Agent 定义
│   ├── data_engineer.py   # 数据工程师 Agent
│   ├── biz_analyst.py     # 业务分析师 Agent
│   └── reporter.py        # 报告撰写员 Agent
│
├── tools/                 # 工具层
│   ├── sql_tool.py        # SQL 连接和执行工具
│   ├── nl2sql.py          # 自然语言转 SQL 工具
│   └── insight.py         # 数据洞察提取工具
│
└── report/               # 报告输出目录
    └── output/           # 生成的报告文件
```

## 🚀 快速开始

### 1. 环境准备

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

创建 `.env` 文件，添加以下配置：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-4o-mini

# MySQL 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chinook
```

### 2. 准备数据库

本项目使用 Chinook 示例数据库（音乐商店数据）。

#### 下载 Chinook 数据库

```bash
# 下载 Chinook MySQL 脚本
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_MySql.sql

# 导入数据库
mysql -u root -p < Chinook_MySql.sql
```

### 3. 运行程序

#### 交互模式（推荐）

```bash
python main.py
```

进入交互式问答模式，系统会提示您输入问题。

#### 单问题模式

```bash
python main.py "哪个国家的客户消费最多？"
```

#### 演示模式

```bash
python main.py demo
```

运行预设的示例问题。

#### 批量分析模式

```bash
# 创建问题文件
echo "哪个国家的客户消费最多？" > questions.txt
echo "收入最高的艺人TOP10？" >> questions.txt

# 运行批量分析
python main.py batch questions.txt
```

## 📊 支持的问题类型

基于 Chinook 数据库，系统支持以下类型的分析问题：

1. **国家/地区分析**

   - "哪个国家的客户消费最多？"
   - "TOP 5 消费国家排名？"

2. **艺人/专辑分析**

   - "收入最高的艺人 TOP10？"
   - "哪个艺人的专辑最多？"

3. **统计指标**

   - "平均每张发票金额是多少？"
   - "总销售额是多少？"

4. **趋势分析**

   - "按月份汇总的销售趋势？"
   - "2023 年的销售情况？"

5. **流派分析**
   - "最受欢迎的音乐流派？"
   - "不同流派的销售对比？"

### 🆕 v2.0 新增：支持任意问题！

#### 🎵 MySQL/Chinook 数据库（无限制）

不再局限于预设问题！现在支持任意自然语言查询：

**示例新问题**：

- "有多少个客户？"
- "哪个艺人的专辑数量最多但销售不佳？"
- "找出购买过 Rock 流派音乐的客户数量"
- "计算每个城市的客户平均消费"
- "哪些员工的销售业绩最好？"
- "2023 年第一季度的收入是多少？"

#### 📁 CSV 文件数据源（全新功能）

现在支持分析本地 CSV 文件！

**内置示例数据**：

- `data/sales.csv` - 销售数据（产品、订单、地区）
- `data/employees.csv` - 员工数据（部门、薪资、职位）

**CSV 问题示例**：

- "销售额最高的产品是什么？"
- "技术部有多少员工？"
- "华东地区的总销售额是多少？"
- "平均薪资最高的部门是哪个？"

**添加自己的 CSV**：

1. 将 CSV 文件放入 `data/` 目录
2. 系统自动加载
3. 直接提问即可！

## 🔧 架构详解

### 数据流（Flow）

```
用户问题
   ↓
DataEngineer Agent
   ├─→ nl2sql: 自然语言 → SQL
   └─→ sql_query_md: 执行 SQL → Markdown 表格
   ↓
BizAnalyst Agent
   └─→ summarize_table: 提取业务洞察
   ↓
Reporter Agent
   └─→ 组装最终报告
   ↓
Markdown 报告（保存到 report/output/）
```

### Agent 职责

#### 1. DataEngineer（数据工程师）

**目标**: 将业务问题转换为 SQL 查询并执行

**工具**:

- `nl2sql`: 自然语言转 SQL（基于规则）
- `sql_query_md`: 执行 SQL 并返回 Markdown 表格
- `get_database_schema`: 获取数据库架构信息

**输出**: Markdown 格式的查询结果表格

#### 2. BizAnalyst（业务分析师）

**目标**: 从数据中提取关键业务洞察

**工具**:

- `summarize_table`: 分析表格并提取洞察
- `calculate_kpi`: 计算业务 KPI

**输出**: 2-3 条关键业务洞察

#### 3. Reporter（报告撰写员）

**目标**: 生成结构化的管理层报告

**工具**: 无（仅组织信息）

**输出**: 完整的 Markdown 格式报告

### 工具层（Tools）

#### sql_tool.py - SQL 工具

- **安全性**: 只允许 SELECT 查询，阻止危险关键字
- **连接管理**: SQLAlchemy 连接池
- **输出格式**: Markdown 表格

#### nl2sql.py - NL2SQL 转换

- **规则引擎**: 基于关键字匹配的模式识别
- **可扩展**: 易于添加新的查询模式
- **未来升级**: 可集成 LLM 进行智能转换

#### insight.py - 洞察提取

- **自动分析**: TOP 项识别、数值分析、分布特征
- **KPI 计算**: 增长率、利润率、平均值等
- **可读性**: 使用表情符号增强展示

## 📝 示例输出

### 问题示例

"哪个国家的客户消费最多？"

### 报告示例

```markdown
# 数据分析报告

## 📋 分析问题

哪个国家的客户消费最多？

## 📊 数据查询结果

| 国家   | 客户数量 | 总消费金额 | 平均订单金额 |
| ------ | -------- | ---------- | ------------ |
| USA    | 13       | 1040.49    | 80.04        |
| Canada | 8        | 535.59     | 66.95        |
| France | 5        | 389.07     | 77.81        |

...

## 💡 关键业务洞察

📊 数据概览：共发现 24 条记录。

🏆 TOP 1 国家：USA，总消费金额 为 1040.49。

💰 总消费金额分析：TOP 1 占总体的 19.8%，显示出相对均衡的分布。

## 🎯 建议与行动项

1. **聚焦美国市场**：美国客户贡献最高营收，建议加大营销投入
2. **拓展加拿大市场**：加拿大客单价高，具有增长潜力
3. **优化客户分布**：考虑在低渗透国家推广业务
```

## 🔐 安全特性

1. **只读查询**: 仅允许 SELECT 语句，禁止 INSERT/UPDATE/DELETE
2. **关键字过滤**: 检测并阻止危险 SQL 关键字
3. **参数化查询**: 使用 SQLAlchemy 防止 SQL 注入
4. **连接池管理**: 自动处理数据库连接生命周期

## 🎯 扩展方向

### 短期优化

1. **LLM-based NL2SQL**: 集成 LangChain Text2SQL 提升转换准确性
2. **更多 KPI 工具**: 添加同比/环比、RFM 分析等
3. **图表生成**: 使用 Plotly/Matplotlib 生成可视化图表
4. **PDF 导出**: 使用 WeasyPrint 导出 PDF 报告

### 中期扩展

1. **支持更多数据库**: PostgreSQL、MongoDB、ClickHouse
2. **实时数据源**: 接入 API、实时数仓
3. **自定义模板**: Jinja2 模板引擎支持自定义报告格式
4. **Web UI**: 使用 Streamlit/Gradio 构建交互界面

### 长期规划

1. **多轮对话**: 支持追问和上下文理解
2. **自动调度**: 定时生成周报/月报
3. **权限管理**: 多用户、多角色权限控制
4. **知识库**: 构建业务知识图谱辅助分析

## 🐛 常见问题

### 1. 数据库连接失败

```
❌ 数据库连接失败: Access denied for user
```

**解决**: 检查 `.env` 中的数据库配置是否正确

### 2. OpenAI API 错误

```
❌ OpenAI API Error: Rate limit exceeded
```

**解决**: 检查 API 密钥是否有效，或更换为 gpt-4o-mini 降低成本

### 3. 无法识别问题

```
无法识别问题，请尝试以下类型的问题...
```

**解决**: 参考"支持的问题类型"重新提问，或在 `nl2sql.py` 中添加新模式

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
