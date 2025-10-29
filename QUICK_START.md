# 快速开始

## 安装

```bash
pip install -r requirements.txt
```

## 配置

创建 `config.py`：

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

## 启动

```bash
# 一键启动
start_all.bat

# 或分别启动
start_api.bat  # API 服务
start_web.bat  # Web 界面
```

访问 http://localhost:8080

## 使用

### Web 界面

输入自然语言问题，例如：

- 哪个国家的客户消费最多？
- 收入最高的艺人 TOP 10？
- 最受欢迎的音乐流派是什么？

### 命令行

```bash
python ask_agent.py "哪个国家的客户消费最多？"
```

### API

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"question": "哪个国家的客户消费最多？"}
)
```

## Power BI

```bash
# 生成数据
python generate_powerbi_data.py

# Power BI 中连接
# 获取数据 → Web → http://localhost:8000/api/v1/history
```

## 常见问题

**API 启动失败？**
检查 MySQL 是否运行，`config.py` 配置是否正确。

**Web 界面一直加载？**
分析需要 30-60 秒，按 F12 查看控制台。

**如何切换数据库？**
修改 `config.py` 中的 `DB_CONFIG`。

## 更多

详细文档：[README.md](README.md)
