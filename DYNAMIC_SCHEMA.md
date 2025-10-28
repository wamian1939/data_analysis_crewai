# 🔄 动态 Schema 读取功能

## 🎯 解决的问题

**之前**：每次更换数据库，都需要手动修改 `tools/nl2sql.py` 中的 `CHINOOK_SCHEMA` 常量。

**现在**：系统自动从数据库读取表结构，**无需手动维护**！

## ✨ 功能特性

### 1. 自动读取数据库结构

```python
# 系统会自动：
# 1. 连接到数据库
# 2. 读取所有表名
# 3. 读取每个表的列信息（类型、主键、外键等）
# 4. 生成格式化的 Schema 描述
# 5. 缓存结果提高性能
```

### 2. 智能缓存机制

- 首次查询时读取并缓存
- 后续查询直接使用缓存（极快）
- 支持手动刷新（数据库结构变化时）

### 3. 向后兼容

- 如果动态读取失败，自动回退到静态 Schema
- 不影响现有功能

## 📝 使用方法

### 方法 1：无需任何配置（推荐）

直接使用！系统会自动从数据库读取 Schema：

```bash
# 切换到新数据库
# 1. 修改 config.py 中的 DB_CONFIG
DB_CONFIG = {
    "database": "your_new_database",  # 改成新数据库
    ...
}

# 2. 直接运行，无需其他配置
python main.py "您的数据库有哪些表？"
```

**就是这么简单！**

### 方法 2：查看自动读取的 Schema

如果想确认系统读取到了什么：

```python
# 在 Python 中测试
from tools.schema_reader import get_dynamic_schema

# 查看完整 Schema
print(get_dynamic_schema())

# 查看智能 Schema（包含统计信息）
from tools.schema_reader import get_smart_schema
print(get_smart_schema())
```

### 方法 3：刷新 Schema 缓存

如果数据库结构改变了（添加/删除表或列）：

```bash
# 方式 1：通过 Agent 刷新
python main.py "刷新数据库结构"

# 方式 2：在代码中刷新
from tools.schema_reader import get_cached_schema
schema = get_cached_schema(force_refresh=True)
```

## 🔧 工作原理

### 架构图

```
用户问题
    ↓
nl2sql 工具
    ↓
检查是否需要 Schema
    ↓
schema_reader.py
    ├─ 连接数据库（复用现有连接）
    ├─ 使用 SQLAlchemy Inspection
    ├─ 读取表结构
    ├─ 格式化输出
    └─ 缓存结果
    ↓
传递给 LLM
    ↓
生成 SQL
```

### 核心代码

**自动读取 Schema**：

```python
# tools/schema_reader.py
def get_dynamic_schema():
    db = get_db()  # 复用现有数据库连接
    inspector = inspect(db.engine)

    # 获取所有表
    for table in inspector.get_table_names():
        # 获取列信息
        columns = inspector.get_columns(table)
        # 获取主键、外键等
        ...
```

**使用动态 Schema**：

```python
# tools/nl2sql.py
def generate_sql_with_llm(question, use_dynamic=True):
    if use_dynamic:
        schema = get_cached_schema()  # 自动读取
    else:
        schema = FALLBACK_SCHEMA  # 后备方案（仅在无法连接数据库时）

    # 生成 SQL...
```

## 💡 实际应用示例

### 示例 1：切换到不同的数据库

**场景**：从 Chinook 切换到您的业务数据库

```python
# 1. 修改 config.py
DB_CONFIG = {
    "database": "my_business_db",
    ...
}

# 2. 直接使用（无需修改代码）
python main.py "我的数据库有多少客户？"
```

**系统自动**：

- ✅ 读取 my_business_db 的表结构
- ✅ 识别客户相关的表
- ✅ 生成正确的 SQL
- ✅ 返回查询结果

### 示例 2：多数据库切换

```python
# config.py 中定义多个数据库
DB_CONFIG_MAIN = {"database": "main_db"}
DB_CONFIG_TEST = {"database": "test_db"}

# 在代码中切换
from tools.sql_tool import SQLDatabase
db = SQLDatabase()
# ... 切换逻辑
```

### 示例 3：查看数据库结构

```bash
# 让 Agent 告诉你数据库里有什么
python main.py "数据库里有哪些表？每个表有什么字段？"

# 系统会自动使用 get_schema_info() 工具
```

## 📊 性能对比

| 操作       | 静态 Schema    | 动态 Schema         |
| ---------- | -------------- | ------------------- |
| 首次查询   | 即时           | ~100ms（读取+缓存） |
| 后续查询   | 即时           | 即时（使用缓存）    |
| 切换数据库 | 需要手动改代码 | 自动适应            |
| 维护成本   | 高（手动更新） | 低（自动同步）      |

## 🎓 技术细节

### 使用的技术

1. **SQLAlchemy Inspection API**

   - `inspect(engine)` - 数据库反射
   - `get_table_names()` - 获取表名
   - `get_columns()` - 获取列信息
   - `get_pk_constraint()` - 获取主键
   - `get_foreign_keys()` - 获取外键

2. **缓存机制**

   - 全局变量缓存
   - 首次读取后缓存
   - 支持强制刷新

3. **错误处理**
   - 失败自动回退到静态 Schema
   - 不影响系统运行

### Schema 格式

**简单格式**：

```
1. users (表)
   - id (INTEGER, PRIMARY KEY)
   - name (VARCHAR)
   - email (VARCHAR)
```

**智能格式**（包含统计）：

```
## users
行数: 1500

字段:
🔑 id: INTEGER
   name: VARCHAR(100)
   email: VARCHAR(255)
```

## ⚙️ 高级配置（可选）

### 自定义 Schema 格式

如果需要修改 Schema 输出格式，编辑 `tools/schema_reader.py`：

```python
def _format_schema_for_llm(schema_data):
    # 自定义格式化逻辑
    # 例如：添加示例数据、统计信息等
    ...
```

## 🐛 故障排查

### 问题 1：无法读取 Schema

**错误**：`读取数据库结构失败`

**解决**：

1. 检查数据库连接
2. 确认数据库权限（需要 SELECT 权限）
3. 查看错误详情

### 问题 2：Schema 不完整

**原因**：某些数据库特性不支持

**解决**：

- 使用 `get_smart_schema()` 尝试其他格式
- 或手动补充静态 Schema

### 问题 3：性能问题

**现象**：首次查询较慢

**解决**：

- 正常现象（只在首次查询时读取）
- 后续查询使用缓存，极快
- 或预热：启动时主动调用一次

## 🔮 未来计划

- [ ] 支持 PostgreSQL 特性
- [ ] 支持视图（Views）
- [ ] 支持存储过程
- [ ] Schema 版本管理
- [ ] 多数据库并行查询
- [ ] Schema 可视化

## 📞 反馈

有问题或建议？欢迎提 Issue！

---

**版本**：v2.1  
**更新日期**：2025-01-XX
