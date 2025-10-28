"""
SQL Tool - 安全的只读 SQL 查询工具
连接 MySQL/Chinook 数据库，执行 SELECT 语句并返回 Markdown 表格
"""
import os
import re
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from crewai.tools import tool

# 尝试从 config.py 导入配置，如果失败则从环境变量读取
try:
    from config import DB_CONFIG
    USE_CONFIG_FILE = True
except ImportError:
    USE_CONFIG_FILE = False
    from dotenv import load_dotenv
    load_dotenv()


class SQLDatabase:
    """MySQL 数据库连接管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        if USE_CONFIG_FILE:
            # 从 config.py 读取配置
            self.host = DB_CONFIG["host"]
            self.port = DB_CONFIG["port"]
            self.user = DB_CONFIG["user"]
            self.password = DB_CONFIG["password"]
            self.database = DB_CONFIG["database"]
        else:
            # 从环境变量读取配置
            self.host = os.getenv("DB_HOST", "localhost")
            self.port = os.getenv("DB_PORT", "3306")
            self.user = os.getenv("DB_USER", "root")
            self.password = os.getenv("DB_PASSWORD", "")
            self.database = os.getenv("DB_NAME", "chinook")
        
        # 构建连接字符串
        connection_string = (
            f"mysql+mysqlconnector://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
        
        try:
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            print(f"✅ 成功连接到数据库: {self.database}")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """执行 SQL 查询并返回 DataFrame"""
        with self.engine.connect() as conn:
            result = pd.read_sql(text(query), conn)
        return result
    
    def get_tables(self) -> list:
        """获取数据库中所有表名"""
        query = "SHOW TABLES"
        df = self.execute_query(query)
        return df.iloc[:, 0].tolist()
    
    def get_table_schema(self, table_name: str) -> str:
        """获取表结构信息"""
        query = f"DESCRIBE {table_name}"
        df = self.execute_query(query)
        return df.to_markdown(index=False)


# 全局数据库实例
_db_instance: Optional[SQLDatabase] = None


def get_db() -> SQLDatabase:
    """获取数据库单例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SQLDatabase()
    return _db_instance


def is_safe_query(query: str) -> tuple[bool, str]:
    """
    检查 SQL 查询是否安全（只允许 SELECT）
    返回: (是否安全, 错误信息)
    """
    query_upper = query.strip().upper()
    
    # 只允许 SELECT 语句
    if not query_upper.startswith("SELECT"):
        return False, "❌ 只允许 SELECT 查询语句"
    
    # 禁止的关键字
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", 
        "ALTER", "TRUNCATE", "GRANT", "REVOKE"
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"❌ 检测到危险关键字: {keyword}"
    
    return True, "✅ 查询安全"


@tool("sql_query_md")
def sql_query_md(query: str) -> str:
    """
    执行 SQL 查询并返回 Markdown 格式的表格
    
    参数:
        query: SQL SELECT 查询语句
    
    返回:
        Markdown 格式的查询结果表格
    
    示例:
        SELECT * FROM customers LIMIT 10
    """
    try:
        # 安全性检查
        is_safe, message = is_safe_query(query)
        if not is_safe:
            return f"错误: {message}\n\n请只使用 SELECT 语句查询数据。"
        
        # 执行查询
        db = get_db()
        df = db.execute_query(query)
        
        # 如果结果为空
        if df.empty:
            return "查询结果为空，未找到匹配的数据。"
        
        # 转换为 Markdown 表格
        markdown_table = df.to_markdown(index=False)
        result = f"查询成功！共返回 {len(df)} 行数据：\n\n{markdown_table}"
        
        return result
        
    except SQLAlchemyError as e:
        return f"SQL 执行错误: {str(e)}\n\n请检查 SQL 语法是否正确。"
    except Exception as e:
        return f"未知错误: {str(e)}"


@tool("get_database_schema")
def get_database_schema(table_name: Optional[str] = None) -> str:
    """
    获取数据库架构信息
    
    参数:
        table_name: 可选，指定表名获取该表的结构；不指定则返回所有表名
    
    返回:
        数据库架构信息（Markdown 格式）
    """
    try:
        db = get_db()
        
        if table_name:
            # 返回指定表的结构
            schema = db.get_table_schema(table_name)
            return f"表 `{table_name}` 的结构：\n\n{schema}"
        else:
            # 返回所有表名
            tables = db.get_tables()
            tables_str = "\n".join([f"- {table}" for table in tables])
            return f"数据库中的表：\n\n{tables_str}"
            
    except Exception as e:
        return f"获取数据库架构失败: {str(e)}"

