"""
Schema Reader - 动态数据库结构读取工具
自动从数据库中读取表结构，无需手动维护
"""
from sqlalchemy import inspect, MetaData, text
from tools.sql_tool import get_db


def get_dynamic_schema(detailed: bool = True) -> str:
    """
    动态从数据库中读取完整的表结构
    
    参数:
        detailed: 是否包含详细的列信息（类型、主键、外键等）
    
    返回:
        格式化的数据库结构描述
    """
    try:
        db = get_db()
        inspector = inspect(db.engine)
        
        schema_lines = []
        schema_lines.append("数据库表结构（自动读取）：\n")
        
        # 获取所有表名
        table_names = inspector.get_table_names()
        
        if not table_names:
            return "数据库中没有表"
        
        # 遍历每个表
        for idx, table_name in enumerate(table_names, 1):
            schema_lines.append(f"{idx}. {table_name} (表)")
            
            if detailed:
                # 获取列信息
                columns = inspector.get_columns(table_name)
                
                # 获取主键
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint.get('constrained_columns', [])
                
                # 获取外键
                foreign_keys = inspector.get_foreign_keys(table_name)
                fk_columns = {fk['constrained_columns'][0]: fk['referred_table'] 
                             for fk in foreign_keys if fk['constrained_columns']}
                
                # 格式化列信息
                for col in columns:
                    col_name = col['name']
                    col_type = str(col['type'])
                    
                    # 构建列描述
                    col_desc = f"   - {col_name} ({col_type}"
                    
                    # 添加约束信息
                    constraints = []
                    if col_name in primary_keys:
                        constraints.append("PRIMARY KEY")
                    if col_name in fk_columns:
                        constraints.append(f"FOREIGN KEY -> {fk_columns[col_name]}")
                    if not col.get('nullable', True):
                        constraints.append("NOT NULL")
                    
                    if constraints:
                        col_desc += f", {', '.join(constraints)}"
                    
                    col_desc += ")"
                    schema_lines.append(col_desc)
            
            schema_lines.append("")  # 空行分隔
        
        # 添加表数量统计
        schema_lines.insert(1, f"共 {len(table_names)} 个表\n")
        
        return "\n".join(schema_lines)
        
    except Exception as e:
        return f"读取数据库结构失败: {str(e)}"


def get_table_sample_data(table_name: str, limit: int = 3) -> str:
    """
    获取表的示例数据，帮助 LLM 理解表内容
    
    参数:
        table_name: 表名
        limit: 返回的样本行数
    
    返回:
        示例数据的文本描述
    """
    try:
        db = get_db()
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        
        with db.engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            
            if not rows:
                return f"表 {table_name} 为空"
            
            # 获取列名
            columns = result.keys()
            
            # 格式化示例数据
            lines = [f"表 {table_name} 的示例数据（前 {len(rows)} 行）："]
            lines.append(f"列: {', '.join(columns)}")
            lines.append("")
            
            for i, row in enumerate(rows, 1):
                row_data = [f"{col}={row[col]}" for col in columns]
                lines.append(f"行{i}: {', '.join(row_data)}")
            
            return "\n".join(lines)
            
    except Exception as e:
        return f"获取示例数据失败: {str(e)}"


def get_smart_schema(include_samples: bool = False) -> str:
    """
    获取智能 Schema（推荐用于 LLM）
    结合表结构和统计信息，提供更好的上下文
    
    参数:
        include_samples: 是否包含示例数据
    
    返回:
        智能 Schema 描述
    """
    try:
        db = get_db()
        inspector = inspect(db.engine)
        
        schema_lines = []
        schema_lines.append("=== 数据库结构（智能分析） ===\n")
        
        table_names = inspector.get_table_names()
        
        for table_name in table_names:
            # 获取表的行数
            with db.engine.connect() as conn:
                count_query = f"SELECT COUNT(*) as cnt FROM {table_name}"
                result = conn.execute(text(count_query))
                row_count = result.fetchone()[0]
            
            schema_lines.append(f"## {table_name}")
            schema_lines.append(f"行数: {row_count}")
            schema_lines.append("")
            
            # 列信息
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            primary_keys = pk_constraint.get('constrained_columns', [])
            
            schema_lines.append("字段:")
            for col in columns:
                col_name = col['name']
                col_type = str(col['type'])
                
                marker = "🔑" if col_name in primary_keys else "  "
                schema_lines.append(f"{marker} {col_name}: {col_type}")
            
            # 可选：添加示例数据
            if include_samples and row_count > 0:
                schema_lines.append("")
                sample = get_table_sample_data(table_name, limit=2)
                schema_lines.append(sample)
            
            schema_lines.append("\n" + "-" * 50 + "\n")
        
        return "\n".join(schema_lines)
        
    except Exception as e:
        return f"生成智能 Schema 失败: {str(e)}"


# 缓存 schema，避免重复查询
_schema_cache = None
_smart_schema_cache = None


def get_cached_schema(force_refresh: bool = False) -> str:
    """
    获取缓存的 Schema（提高性能）
    
    参数:
        force_refresh: 是否强制刷新缓存
    
    返回:
        Schema 描述
    """
    global _schema_cache
    
    if _schema_cache is None or force_refresh:
        _schema_cache = get_dynamic_schema(detailed=True)
    
    return _schema_cache


def get_cached_smart_schema(force_refresh: bool = False) -> str:
    """
    获取缓存的智能 Schema
    
    参数:
        force_refresh: 是否强制刷新缓存
    
    返回:
        智能 Schema 描述
    """
    global _smart_schema_cache
    
    if _smart_schema_cache is None or force_refresh:
        _smart_schema_cache = get_smart_schema(include_samples=False)
    
    return _smart_schema_cache


# 导出
__all__ = [
    'get_dynamic_schema',
    'get_table_sample_data', 
    'get_smart_schema',
    'get_cached_schema',
    'get_cached_smart_schema'
]

