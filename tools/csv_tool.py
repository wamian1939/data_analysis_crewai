"""
CSV Tool - CSV 文件数据查询和分析工具
支持读取本地 CSV 文件，执行类似 SQL 的查询操作
"""
import os
import pandas as pd
from crewai.tools import tool
from typing import Optional


class CSVDatabase:
    """CSV 文件数据管理类"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化 CSV 数据库
        
        参数:
            data_dir: CSV 文件所在目录
        """
        self.data_dir = data_dir
        self.dataframes = {}  # 缓存加载的 DataFrame
        self.file_schemas = {}  # 存储文件结构信息
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 自动发现并加载 CSV 文件
        self._discover_csv_files()
    
    def _discover_csv_files(self):
        """自动发现数据目录中的所有 CSV 文件"""
        if not os.path.exists(self.data_dir):
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.data_dir, filename)
                table_name = filename[:-4]  # 移除 .csv 扩展名
                try:
                    self.load_csv(table_name, filepath)
                    print(f"✓ 已加载 CSV 文件: {filename} -> 表名: {table_name}")
                except Exception as e:
                    print(f"✗ 加载失败 {filename}: {e}")
    
    def load_csv(self, table_name: str, filepath: str):
        """
        加载 CSV 文件到内存
        
        参数:
            table_name: 表名（用于引用）
            filepath: CSV 文件路径
        """
        df = pd.read_csv(filepath)
        self.dataframes[table_name] = df
        
        # 记录表结构
        schema_info = {
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'rows': len(df),
            'filepath': filepath
        }
        self.file_schemas[table_name] = schema_info
    
    def get_tables(self) -> list:
        """获取所有已加载的表名"""
        return list(self.dataframes.keys())
    
    def get_table_schema(self, table_name: str) -> str:
        """
        获取表结构信息
        
        参数:
            table_name: 表名
        
        返回:
            表结构的文本描述
        """
        if table_name not in self.file_schemas:
            return f"表 '{table_name}' 不存在"
        
        schema = self.file_schemas[table_name]
        lines = [
            f"表名: {table_name}",
            f"文件: {schema['filepath']}",
            f"行数: {schema['rows']}",
            f"\n列信息:"
        ]
        
        for col in schema['columns']:
            dtype = schema['dtypes'][col]
            lines.append(f"  - {col} ({dtype})")
        
        return "\n".join(lines)
    
    def get_all_schemas(self) -> str:
        """获取所有表的结构信息"""
        if not self.dataframes:
            return "未找到任何 CSV 文件。请将 CSV 文件放在 'data/' 目录中。"
        
        schemas = []
        for table_name in self.dataframes.keys():
            schemas.append(self.get_table_schema(table_name))
            schemas.append("-" * 50)
        
        return "\n".join(schemas)
    
    def query(self, table_name: str, conditions: Optional[dict] = None, 
              columns: Optional[list] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        简单查询 CSV 数据
        
        参数:
            table_name: 表名
            conditions: 过滤条件 (字典格式)
            columns: 要选择的列
            limit: 限制返回行数
        
        返回:
            查询结果 DataFrame
        """
        if table_name not in self.dataframes:
            raise ValueError(f"表 '{table_name}' 不存在")
        
        df = self.dataframes[table_name].copy()
        
        # 应用过滤条件
        if conditions:
            for col, value in conditions.items():
                df = df[df[col] == value]
        
        # 选择列
        if columns:
            df = df[columns]
        
        # 限制行数
        if limit:
            df = df.head(limit)
        
        return df


# 全局 CSV 数据库实例
_csv_db: Optional[CSVDatabase] = None


def get_csv_db() -> CSVDatabase:
    """获取 CSV 数据库单例"""
    global _csv_db
    if _csv_db is None:
        _csv_db = CSVDatabase()
    return _csv_db


@tool("csv_query")
def csv_query(table_name: str, limit: int = 100) -> str:
    """
    查询 CSV 表数据并返回 Markdown 格式
    
    参数:
        table_name: CSV 表名（不含 .csv 扩展名）
        limit: 返回的最大行数（默认 100）
    
    返回:
        Markdown 格式的查询结果
    
    示例:
        csv_query("sales", limit=10)
        csv_query("customers")
    """
    try:
        db = get_csv_db()
        
        if table_name not in db.dataframes:
            available = ", ".join(db.get_tables())
            return f"表 '{table_name}' 不存在。\n可用的表: {available}"
        
        df = db.query(table_name, limit=limit)
        
        if df.empty:
            return f"表 '{table_name}' 为空或查询结果为空"
        
        markdown_table = df.to_markdown(index=False)
        result = f"查询成功！表 '{table_name}' 共 {len(df)} 行数据：\n\n{markdown_table}"
        
        return result
        
    except Exception as e:
        return f"CSV 查询失败: {str(e)}"


@tool("get_csv_schema")
def get_csv_schema(table_name: Optional[str] = None) -> str:
    """
    获取 CSV 表结构信息
    
    参数:
        table_name: 表名（可选）。如果不指定，返回所有表的结构
    
    返回:
        表结构信息（Markdown 格式）
    """
    try:
        db = get_csv_db()
        
        if table_name:
            return db.get_table_schema(table_name)
        else:
            return db.get_all_schemas()
            
    except Exception as e:
        return f"获取 CSV 架构失败: {str(e)}"


@tool("csv_filter")
def csv_filter(table_name: str, column: str, value: str, limit: int = 50) -> str:
    """
    根据条件过滤 CSV 数据
    
    参数:
        table_name: CSV 表名
        column: 要过滤的列名
        value: 过滤值
        limit: 返回的最大行数
    
    返回:
        过滤后的数据（Markdown 格式）
    """
    try:
        db = get_csv_db()
        
        df = db.query(table_name, conditions={column: value}, limit=limit)
        
        if df.empty:
            return f"未找到满足条件的数据: {column}={value}"
        
        markdown_table = df.to_markdown(index=False)
        result = f"过滤结果（{column}={value}）: {len(df)} 行\n\n{markdown_table}"
        
        return result
        
    except Exception as e:
        return f"CSV 过滤失败: {str(e)}"


# 导出的工具
__all__ = ['csv_query', 'get_csv_schema', 'csv_filter', 'CSVDatabase', 'get_csv_db']

