# 更新日志

## v2.1 - 动态 Schema 读取 + 代码简化

**发布日期**: 2025-10-28

### ✨ 新功能

- **动态 Schema 读取**: 系统自动从数据库读取表结构，无需手动配置
- **智能缓存机制**: 首次读取后缓存 Schema，提升性能
- **一键切换数据库**: 只需修改配置文件，无需改动代码

### 🧹 代码清理

- **删除冗余静态 Schema**: 移除了 `tools/nl2sql.py` 中 200+ 行的 `CHINOOK_SCHEMA` 静态配置
- **简化后备机制**: 将静态 Schema 替换为简洁的 `FALLBACK_SCHEMA`
- **更新文档**: 清理文档中过时的静态 Schema 相关内容

### 📝 文件变更

#### 修改的文件

- `tools/nl2sql.py`: 
  - 删除 `CHINOOK_SCHEMA` (200+ 行)
  - 添加 `FALLBACK_SCHEMA` (简洁提示信息)
  - 更新所有引用
  
- `README.md`:
  - 添加动态 Schema 读取功能说明
  - 更新核心特性部分

- `DYNAMIC_SCHEMA.md`:
  - 更新代码示例
  - 简化配置说明

- `.gitignore`:
  - 添加 `schema_cache.json` (缓存文件)

#### 新增的文件

- `tools/schema_reader.py`: 动态 Schema 读取工具
- `DYNAMIC_SCHEMA.md`: 动态 Schema 功能详细文档
- `CHANGELOG.md`: 本文件

### 🔄 向后兼容

- ✅ 完全向后兼容
- ✅ 如果动态读取失败，自动回退到后备机制
- ✅ 不影响现有功能

### 📊 性能优化

| 指标 | v2.0 (静态) | v2.1 (动态) |
|---|---|---|
| 代码量 | ~300 行 | ~100 行 |
| 维护成本 | 高（手动更新） | 低（自动同步） |
| 切换数据库 | 需修改代码 | 只需修改配置 |
| 首次查询 | 即时 | ~100ms |
| 后续查询 | 即时 | 即时（缓存） |

### 🎯 使用方法

#### 切换到新数据库

```python
# 修改 config.py
DB_CONFIG = {
    "database": "your_database",  # 改成新数据库
    ...
}

# 直接运行，无需其他改动
python main.py "您的问题"
```

#### 刷新 Schema 缓存

```bash
# 方式 1：让 Agent 刷新
python main.py "刷新数据库结构"

# 方式 2：删除缓存文件
rm schema_cache.json
```

### 📖 详细文档

- 动态 Schema 功能: [DYNAMIC_SCHEMA.md](DYNAMIC_SCHEMA.md)
- 项目文档: [README.md](README.md)
- v2.0 升级: [UPGRADE_V2.md](UPGRADE_V2.md)

---

## v2.0 - LLM 驱动 + 多数据源

**发布日期**: 2025-10-27

### ✨ 新功能

- **LLM 驱动的 NL2SQL**: 使用 OpenAI GPT 动态生成 SQL
- **多数据源支持**: MySQL + CSV 文件
- **智能数据源选择**: Agent 自动判断使用哪个数据源

### 📝 详细内容

见 [UPGRADE_V2.md](UPGRADE_V2.md)

---

## v1.0 - 初始版本

**发布日期**: 2025-10-26

### ✨ 功能

- 基于 CrewAI 的多 Agent 协作
- 规则驱动的 NL2SQL
- MySQL/Chinook 数据库查询
- Markdown 报告生成

