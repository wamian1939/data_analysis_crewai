"""
NL2SQL Tool - 智能自然语言转 SQL 查询
使用 LLM 动态生成 SQL，支持任意自然语言问题
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


# Chinook 数据库详细表结构（用于 LLM 理解）
CHINOOK_SCHEMA = """
Chinook 数据库完整表结构：

1. Album (专辑表)
   - AlbumId (INTEGER, PRIMARY KEY): 专辑ID
   - Title (VARCHAR): 专辑标题
   - ArtistId (INTEGER, FOREIGN KEY): 艺人ID

2. Artist (艺人表)
   - ArtistId (INTEGER, PRIMARY KEY): 艺人ID
   - Name (VARCHAR): 艺人名称

3. Customer (客户表)
   - CustomerId (INTEGER, PRIMARY KEY): 客户ID
   - FirstName (VARCHAR): 名
   - LastName (VARCHAR): 姓
   - Company (VARCHAR): 公司
   - Address (VARCHAR): 地址
   - City (VARCHAR): 城市
   - State (VARCHAR): 州/省
   - Country (VARCHAR): 国家
   - PostalCode (VARCHAR): 邮编
   - Phone (VARCHAR): 电话
   - Fax (VARCHAR): 传真
   - Email (VARCHAR): 邮箱
   - SupportRepId (INTEGER): 支持代表ID

4. Employee (员工表)
   - EmployeeId (INTEGER, PRIMARY KEY): 员工ID
   - LastName (VARCHAR): 姓
   - FirstName (VARCHAR): 名
   - Title (VARCHAR): 职位
   - ReportsTo (INTEGER): 上级ID
   - BirthDate (DATETIME): 生日
   - HireDate (DATETIME): 入职日期
   - Address (VARCHAR): 地址
   - City (VARCHAR): 城市
   - State (VARCHAR): 州/省
   - Country (VARCHAR): 国家
   - PostalCode (VARCHAR): 邮编
   - Phone (VARCHAR): 电话
   - Fax (VARCHAR): 传真
   - Email (VARCHAR): 邮箱

5. Genre (流派表)
   - GenreId (INTEGER, PRIMARY KEY): 流派ID
   - Name (VARCHAR): 流派名称

6. Invoice (发票表)
   - InvoiceId (INTEGER, PRIMARY KEY): 发票ID
   - CustomerId (INTEGER, FOREIGN KEY): 客户ID
   - InvoiceDate (DATETIME): 发票日期
   - BillingAddress (VARCHAR): 账单地址
   - BillingCity (VARCHAR): 账单城市
   - BillingState (VARCHAR): 账单州/省
   - BillingCountry (VARCHAR): 账单国家
   - BillingPostalCode (VARCHAR): 账单邮编
   - Total (DECIMAL): 总金额

7. InvoiceLine (发票明细表)
   - InvoiceLineId (INTEGER, PRIMARY KEY): 明细ID
   - InvoiceId (INTEGER, FOREIGN KEY): 发票ID
   - TrackId (INTEGER, FOREIGN KEY): 音轨ID
   - UnitPrice (DECIMAL): 单价
   - Quantity (INTEGER): 数量

8. Track (音轨表)
   - TrackId (INTEGER, PRIMARY KEY): 音轨ID
   - Name (VARCHAR): 音轨名称
   - AlbumId (INTEGER, FOREIGN KEY): 专辑ID
   - MediaTypeId (INTEGER): 媒体类型ID
   - GenreId (INTEGER, FOREIGN KEY): 流派ID
   - Composer (VARCHAR): 作曲家
   - Milliseconds (INTEGER): 时长（毫秒）
   - Bytes (INTEGER): 文件大小
   - UnitPrice (DECIMAL): 单价

9. MediaType (媒体类型表)
   - MediaTypeId (INTEGER, PRIMARY KEY): 媒体类型ID
   - Name (VARCHAR): 类型名称

10. Playlist (播放列表表)
    - PlaylistId (INTEGER, PRIMARY KEY): 播放列表ID
    - Name (VARCHAR): 列表名称

11. PlaylistTrack (播放列表-音轨关联表)
    - PlaylistId (INTEGER, FOREIGN KEY): 播放列表ID
    - TrackId (INTEGER, FOREIGN KEY): 音轨ID
"""


def generate_sql_with_llm(question: str, schema: str = CHINOOK_SCHEMA) -> str:
    """
    使用 LLM 将自然语言问题转换为 SQL 查询
    
    参数:
        question: 用户的自然语言问题
        schema: 数据库表结构描述
    
    返回:
        SQL 查询语句
    """
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
def get_schema_info() -> str:
    """
    获取 Chinook 数据库的完整表结构信息
    
    返回:
        数据库架构描述（包含所有表和字段）
    """
    return CHINOOK_SCHEMA


# 导出的工具
__all__ = ['nl2sql', 'get_schema_info', 'generate_sql_with_llm', 'CHINOOK_SCHEMA']
