"""
配置文件示例
使用说明：
1. 复制此文件并重命名为 config.py
2. 填入您的真实 API 密钥和数据库密码
3. config.py 不会被提交到 Git（已在 .gitignore 中）
"""

# ====================================
# OpenAI API 配置
# ====================================
OPENAI_API_KEY = "sk-your-api-key-here"  # 替换为您的真实 OpenAI API Key
OPENAI_MODEL_NAME = "gpt-4o-mini"

# 可选：自定义 API 端点（如使用代理）
# OPENAI_API_BASE = "https://api.openai.com/v1"

# ====================================
# MySQL 数据库配置
# ====================================
DB_CONFIG = {
    "user": "root",              # 替换为您的 MySQL 用户名
    "password": "your_password",  # 替换为您的 MySQL 密码
    "host": "127.0.0.1",         # 数据库主机地址
    "port": 3306,                # 数据库端口
    "database": "chinook",       # 数据库名称
}

# ====================================
# 其他配置
# ====================================
# 日志级别
LOG_LEVEL = "INFO"

# 报告输出目录
REPORT_OUTPUT_DIR = "report/output"

# CrewAI 配置
CREW_VERBOSE = True  # 是否显示详细日志

