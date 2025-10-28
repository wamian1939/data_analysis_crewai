"""
NL2SQL Tool - 智能自然语言转 SQL 查询
使用 LLM 动态生成 SQL，支持任意自然语言问题
✨ v2.1: 支持动态读取数据库 Schema，无需手动维护
"""
from crewai.tools import tool
import re
import os

# 尝试导入配置
try:
    from config import OPENAI_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
except ImportError:
    pass

from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI()

# 导入动态 Schema 读取器
try:
    from tools.schema_reader import get_cached_schema, get_cached_smart_schema
    USE_DYNAMIC_SCHEMA = True
except ImportError:
    USE_DYNAMIC_SCHEMA = False
    print("[警告] 无法导入 schema_reader，将使用静态 Schema")


# 静态 Schema（仅作为后备，优先使用动态读取）
FALLBACK_SCHEMA = """
无法动态读取数据库结构。
请检查数据库连接或使用 get_schema_info() 工具查看表结构。
"""


def generate_sql_with_llm(question: str, schema: str = None, use_dynamic: bool = True) -> str:
    """
    使用 LLM 将自然语言问题转换为 SQL 查询
    
    参数:
        question: 用户的自然语言问题
        schema: 数据库表结构描述（可选，如果不提供则自动读取）
        use_dynamic: 是否使用动态 Schema（默认 True）
    
    返回:
        SQL 查询语句
    """
    # 决定使用哪个 schema
    if schema is None:
        if use_dynamic and USE_DYNAMIC_SCHEMA:
            # 使用动态读取的 schema（推荐）
            try:
                schema = get_cached_schema()
                print("[NL2SQL] ✅ 使用动态读取的数据库 Schema")
            except Exception as e:
                print(f"[NL2SQL] ❌ 动态读取失败: {e}")
                schema = FALLBACK_SCHEMA
                print("[NL2SQL] 使用后备 Schema（请检查数据库连接）")
        else:
            # 动态读取功能未启用
            schema = FALLBACK_SCHEMA
            print("[NL2SQL] ⚠️ 动态 Schema 功能未启用，请安装 schema_reader")
    
    system_prompt = f"""你是一个 SQL 专家。根据用户的自然语言问题和数据库表结构，生成准确的 MySQL SELECT 查询。

数据库表结构：
{schema}

要求：
1. 只生成 SELECT 查询语句（禁止 INSERT/UPDATE/DELETE）
2. 使用标准 MySQL 语法
3. 适当使用 JOIN 关联表
4. 添加 LIMIT 限制结果数量（除非明确要求所有数据）
5. 使用中文别名（AS）使结果易读
6. 只返回 SQL 语句，不要任何解释

示例：
问题：哪个国家的客户最多？
SQL: SELECT Country AS 国家, COUNT(*) AS 客户数量 FROM Customer GROUP BY Country ORDER BY 客户数量 DESC LIMIT 10

问题：最贵的音轨是哪首？
SQL: SELECT Name AS 音轨名称, UnitPrice AS 价格 FROM Track ORDER BY UnitPrice DESC LIMIT 1
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.0,  # 使用确定性输出
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        
        # 清理可能的 markdown 格式
        sql = sql.replace("```sql", "").replace("```", "").strip()
        
        return sql
        
    except Exception as e:
        # 如果 LLM 调用失败，返回错误信息
        return f"-- LLM 生成失败: {str(e)}\n-- 请检查 API 配置或网络连接"


class NL2SQLConverter:
    """自然语言到 SQL 的转换器（LLM 增强版）"""
    
    def __init__(self):
        """初始化转换器"""
        self.use_llm = True  # 默认使用 LLM
    
    def convert(self, question: str) -> str:
        """
        将自然语言问题转换为 SQL 查询
        
        参数:
            question: 用户的自然语言问题
        
        返回:
            SQL 查询语句
        """
        if self.use_llm:
            # 优先使用 LLM 生成
            print(f"[NL2SQL] 使用 LLM 生成 SQL...")
            return generate_sql_with_llm(question)
        else:
            # 后备方案：返回提示信息
            return "-- 请启用 LLM 模式或提供更具体的查询"


@tool("nl2sql")
def nl2sql(question: str) -> str:
    """
    将自然语言问题转换为 SQL 查询语句（智能模式）
    
    参数:
        question: 用户的自然语言问题
    
    返回:
        SQL 查询语句
    
    示例:
        - "有多少个客户？"
        - "2023年的总销售额是多少？"
        - "哪个艺人的专辑最多？"
        - "销售额前10的音轨有哪些？"
        - "员工数量按职位分布如何？"
        - "哪个城市的客户消费能力最强？"
    """
    converter = NL2SQLConverter()
    sql = converter.convert(question)
    return sql


@tool("get_schema_info")
def get_schema_info(dynamic: bool = True) -> str:
    """
    获取数据库的完整表结构信息
    
    参数:
        dynamic: 是否动态读取（True=从数据库读取，False=使用静态配置）
    
    返回:
        数据库架构描述（包含所有表和字段）
    """
    if dynamic and USE_DYNAMIC_SCHEMA:
        try:
            return get_cached_schema()
        except Exception as e:
            print(f"[警告] 动态读取失败: {e}")
            return FALLBACK_SCHEMA
    else:
        return FALLBACK_SCHEMA


@tool("refresh_schema")
def refresh_schema() -> str:
    """
    刷新数据库 Schema 缓存（当数据库结构变化时使用）
    
    返回:
        操作结果信息
    """
    if not USE_DYNAMIC_SCHEMA:
        return "动态 Schema 功能未启用"
    
    try:
        from tools.schema_reader import get_cached_schema
        schema = get_cached_schema(force_refresh=True)
        return f"✅ Schema 已刷新\n\n{schema}"
    except Exception as e:
        return f"❌ 刷新失败: {str(e)}"


# 导出的工具
__all__ = [
    'nl2sql', 
    'get_schema_info', 
    'refresh_schema',
    'generate_sql_with_llm'
]
