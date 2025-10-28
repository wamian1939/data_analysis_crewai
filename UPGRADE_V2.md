# 🚀 v2.0 重大升级

## ✨ 新特性概览

### 1. 智能 NL2SQL - 理解任意问题

**升级前（v1.0）**：

- 只支持 5-6 种预设问题模板
- 问题稍有不同就无法识别
- 需要精确匹配关键字

**升级后（v2.0）**：

- 🤖 **使用 LLM 动态生成 SQL**
- 📝 **理解任意自然语言问题**
- 🎯 **自动匹配数据库 schema**
- ✅ **支持复杂的多表关联查询**

**对比示例**：

| v1.0 (固定模板)                      | v2.0 (智能理解)               |
| ------------------------------------ | ----------------------------- |
| ❌ "客户有多少个？" (无法识别)       | ✅ "客户有多少个？"           |
| ❌ "哪个城市消费最高？" (无法识别)   | ✅ "哪个城市消费最高？"       |
| ✅ "哪个国家的客户消费最多？"        | ✅ "哪个国家的客户消费最多？" |
| ❌ "找出 Rock 流派的音轨" (无法识别) | ✅ "找出 Rock 流派的音轨"     |

### 2. 多数据源支持 - CSV 文件分析

**全新功能**：现在可以分析本地 CSV 文件！

#### 📁 CSV 数据源特性

- **自动发现**：自动加载 `data/` 目录中的所有 CSV 文件
- **即插即用**：无需配置，放入 CSV 即可查询
- **智能路由**：Agent 自动判断使用数据库还是 CSV
- **灵活格式**：支持任意结构的 CSV 文件

#### 内置示例数据

```
data/
├── sales.csv        # 销售数据（20 条记录）
├── employees.csv    # 员工数据（10 条记录）
└── README.md        # CSV 使用说明
```

#### 支持的 CSV 操作

- 查询整表数据
- 按条件过滤
- 数据统计分析
- 与数据库数据结合分析（Agent 智能处理）

## 🆚 功能对比表

| 功能                 | v1.0 | v2.0 |
| -------------------- | :--: | :--: |
| **预设问题查询**     |  ✅  |  ✅  |
| **任意问题查询**     |  ❌  |  ✅  |
| **MySQL 数据库**     |  ✅  |  ✅  |
| **CSV 文件**         |  ❌  |  ✅  |
| **LLM 智能生成 SQL** |  ❌  |  ✅  |
| **多数据源路由**     |  ❌  |  ✅  |
| **自定义数据源**     |  ❌  |  ✅  |

## 📝 使用示例

### 示例 1：智能 SQL 生成

**问题**："2023 年第一季度每个月的销售额是多少？"

**v1.0 响应**：

```
无法识别问题，请尝试以下类型的问题：
- 哪个国家的客户消费最多？
- 收入最高的艺人TOP10？
...
```

**v2.0 响应**：

```sql
SELECT
    DATE_FORMAT(InvoiceDate, '%Y-%m') AS 月份,
    SUM(Total) AS 销售额
FROM Invoice
WHERE InvoiceDate BETWEEN '2023-01-01' AND '2023-03-31'
GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
ORDER BY 月份
```

✅ 自动执行并返回结果！

### 示例 2：CSV 文件分析

**问题**："销售额最高的产品是什么？"

**系统自动**：

1. 识别问题涉及"销售"
2. 检查 CSV 文件中是否有 `sales.csv`
3. 查询 CSV 数据
4. 返回分析结果

```markdown
| product    | total_sales |
| ---------- | ----------- |
| 笔记本电脑 | 23996       |
| 手机       | 15996       |
| 平板电脑   | 14994       |
```

### 示例 3：混合数据源

**问题**："对比音乐销售和产品销售，哪个类别更受欢迎？"

**系统自动**：

1. 从 MySQL 查询音乐销售数据
2. 从 CSV 查询产品销售数据
3. 由 BizAnalyst 综合分析
4. 生成对比报告

## 🔧 技术实现

### NL2SQL 升级

**tools/nl2sql.py** - 完全重写

```python
# v1.0: 基于规则的模式匹配
patterns = [
    {"keywords": ["国家", "客户"], "template": "SELECT..."},
    ...
]

# v2.0: LLM 动态生成
def generate_sql_with_llm(question, schema):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content
```

### CSV 工具

**tools/csv_tool.py** - 全新模块

```python
# 主要功能
- CSVDatabase: CSV 文件管理
- csv_query(): 查询 CSV 数据
- get_csv_schema(): 获取 CSV 结构
- csv_filter(): 过滤 CSV 数据
```

### DataEngineer 增强

**agents/data_engineer.py** - 支持多数据源

```python
tools=[
    # SQL 工具
    nl2sql, sql_query_md, get_database_schema,
    # CSV 工具
    csv_query, get_csv_schema, csv_filter
]
```

## 🎯 使用新功能

### 1. 测试智能 SQL 生成

```bash
python main.py "有多少个来自美国的客户？"
python main.py "哪个作曲家的音轨数量最多？"
python main.py "2023年每个季度的收入对比"
```

### 2. 分析 CSV 数据

```bash
python main.py "销售额最高的产品是什么？"
python main.py "技术部的平均薪资是多少？"
python main.py "华东地区的销售情况"
```

### 3. 添加自定义 CSV

```bash
# 1. 准备 CSV 文件
echo "id,name,value" > data/mydata.csv
echo "1,项目A,1000" >> data/mydata.csv

# 2. 直接提问
python main.py "mydata 表中哪个项目的 value 最高？"
```

## ⚙️ 配置要求

### 必需

- OpenAI API Key（用于 LLM 生成 SQL）
- 已配置的 MySQL 数据库（可选）
- Python 3.11+

### 可选

- CSV 文件（放在 `data/` 目录）

## 🐛 已知问题

1. **LLM 生成的 SQL 可能需要优化**
   - 解决方案：系统会自动捕获错误并重试
2. **大型 CSV 文件可能较慢**
   - 建议：单个 CSV 文件不超过 100MB
3. **复杂的多表 CSV 关联**
   - 当前：Agent 会尝试智能处理
   - 未来：计划支持更复杂的 CSV JOIN

## 📈 性能提升

- SQL 生成速度：~2-3 秒（LLM 调用）
- CSV 加载：自动缓存，第二次查询几乎即时
- 查询响应：比 v1.0 更灵活，但需要额外的 LLM 时间

## 🔮 后续计划

- [ ] 支持 Excel 文件（.xlsx）
- [ ] 支持 JSON 数据
- [ ] PostgreSQL 数据库支持
- [ ] CSV 数据的复杂聚合和 JOIN
- [ ] 数据可视化（图表生成）
- [ ] 数据缓存优化

## 📞 反馈

如有问题或建议，请提 Issue！

---

**升级日期**：2025-01-XX  
**版本**：v2.0.0  
**作者**：CrewAI Data Analysis Team
