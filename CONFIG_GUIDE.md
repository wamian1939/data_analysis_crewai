# ⚙️ 配置指南

## 环境变量配置

### 1. 创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
# 在 Windows PowerShell 中
New-Item -Path .env -ItemType File

# 或者直接复制此内容到 .env 文件
```

### 2. 配置内容

```env
# ===========================================
# OpenAI API 配置
# ===========================================
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-4o-mini

# 可选：如果使用代理或其他 API 端点
# OPENAI_API_BASE=https://api.openai.com/v1

# ===========================================
# MySQL 数据库配置（Chinook 示例）
# ===========================================
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=chinook

# ===========================================
# 可选：日志配置
# ===========================================
# LOG_LEVEL=INFO
```

## 数据库准备

### 方案 1：使用 Chinook 示例数据库（推荐）

Chinook 是一个音乐商店示例数据库，包含艺人、专辑、音轨、客户、发票等表。

#### Windows 安装步骤

1. **安装 MySQL**（如果尚未安装）

   ```powershell
   # 使用 Chocolatey
   choco install mysql

   # 或下载安装包
   # https://dev.mysql.com/downloads/mysql/
   ```

2. **下载 Chinook 数据库脚本**

   ```powershell
   # 下载 SQL 脚本
   Invoke-WebRequest -Uri "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_MySql.sql" -OutFile "Chinook_MySql.sql"
   ```

3. **导入数据库**

   ```powershell
   # 方式 1：使用 MySQL 命令行
   mysql -u root -p < Chinook_MySql.sql

   # 方式 2：使用 MySQL Workbench
   # 打开 MySQL Workbench → 执行 SQL 脚本
   ```

4. **验证安装**
   ```sql
   USE chinook;
   SHOW TABLES;
   SELECT COUNT(*) FROM Customer;
   ```

### 方案 2：使用自己的数据库

如果您想使用自己的数据库：

1. 修改 `.env` 中的数据库配置
2. 修改 `tools/nl2sql.py` 中的 `CHINOOK_SCHEMA` 为您的表结构
3. 添加新的 SQL 查询模式

## OpenAI API 获取

### 1. 注册 OpenAI 账号

访问：https://platform.openai.com/signup

### 2. 创建 API Key

1. 登录后访问：https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 复制密钥（只显示一次）
4. 粘贴到 `.env` 文件的 `OPENAI_API_KEY`

### 3. 选择模型

- **gpt-4o-mini**：推荐，性价比高（$0.15/1M tokens）
- **gpt-4o**：更强大但成本更高（$5/1M tokens）
- **gpt-3.5-turbo**：最经济但能力较弱

### 4. 充值

- 访问：https://platform.openai.com/account/billing
- 最低充值 $5

## 依赖包安装

### 推荐：使用虚拟环境

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# 安装依赖
pip install -r requirements.txt
```

### 可能遇到的问题

#### 问题 1：mysqlclient 安装失败

```powershell
# 解决方案：使用 mysql-connector-python（已在 requirements.txt 中）
pip install mysql-connector-python
```

#### 问题 2：pandas 版本冲突

```powershell
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt --upgrade
```

#### 问题 3：CrewAI 安装慢

```powershell
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 验证配置

运行测试脚本验证配置：

```python
# test_config.py
import os
from dotenv import load_dotenv

load_dotenv()

# 检查 OpenAI API
api_key = os.getenv("OPENAI_API_KEY")
print(f"✓ OpenAI API Key: {'已配置' if api_key else '❌ 未配置'}")

# 检查数据库配置
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
print(f"✓ 数据库: {db_host}/{db_name if db_name else '❌ 未配置'}")

# 测试数据库连接
try:
    from tools.sql_tool import get_db
    db = get_db()
    tables = db.get_tables()
    print(f"✓ 数据库连接成功，共 {len(tables)} 个表")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
```

运行：

```powershell
python test_config.py
```

## 快速启动

配置完成后，运行：

```powershell
# 交互模式
python main.py

# 或演示模式
python main.py demo
```

如果一切正常，您将看到：

```
🎯 CrewAI 数据分析系统 - 交互模式
支持的问题类型：
  1. 哪个国家的客户消费最多？
  2. 收入最高的艺人TOP10？
  ...
```

## 故障排查

### 常见错误

1. **`ModuleNotFoundError: No module named 'crewai'`**

   ```powershell
   pip install crewai crewai-tools
   ```

2. **`Access denied for user 'root'@'localhost'`**

   - 检查 MySQL 用户名和密码
   - 确认 MySQL 服务已启动

3. **`Table 'chinook.customer' doesn't exist`**

   - 重新导入 Chinook 数据库
   - 检查数据库名称是否正确

4. **`OpenAI API Error: Invalid API key`**
   - 检查 API 密钥是否正确
   - 确认账户有足够余额

## 获取帮助

- GitHub Issues: 提交问题
- README.md: 查看完整文档
- main.py help: 查看命令行帮助
