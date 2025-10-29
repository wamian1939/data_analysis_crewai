"""
API 业务服务层 - 精简版
只保留核心的分析和存储功能
"""
import os
import sys
import uuid
import time
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, text, Table, Column, Integer, String, Float, DateTime, MetaData, Text
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crew import DataAnalysisCrew
from api.models import QueryHistory, QueryStatus


# ============================================
# 分析服务
# ============================================

class AnalysisService:
    """数据分析服务"""
    
    def __init__(self):
        self.crew = None
    
    def _get_crew(self):
        """延迟初始化 Crew"""
        if self.crew is None:
            print("[AnalysisService] 初始化 DataAnalysisCrew...")
            self.crew = DataAnalysisCrew()
        return self.crew
    
    def _build_context(self, conversation_history: list) -> str:
        """构建对话上下文"""
        if not conversation_history:
            return ""
        
        # 只保留最近3轮对话作为上下文（避免token过多）
        recent_history = conversation_history[-6:]  # 3轮 = 6条消息
        
        context_parts = ["之前的对话历史:"]
        for msg in recent_history:
            role = "用户" if msg.get("role") == "user" else "助手"
            content = msg.get("content", "")
            # 只保留问题和关键洞察，不包含完整数据
            if len(content) > 200:
                content = content[:200] + "..."
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    async def analyze(self, question: str, conversation_history: list = None) -> Dict[str, Any]:
        """
        执行数据分析
        
        参数:
            question: 用户问题
            conversation_history: 对话历史（用于连续对话）
        
        返回:
            分析结果字典
        """
        query_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        start_time = time.time()
        
        try:
            # 构建完整的问题上下文
            full_question = question
            if conversation_history:
                context = self._build_context(conversation_history)
                if context:
                    full_question = f"{context}\n\n当前问题: {question}"
            
            print(f"[AnalysisService] 开始分析: {question}")
            if conversation_history:
                print(f"[AnalysisService] 对话历史: {len(conversation_history)} 条")
            
            # 执行 CrewAI 分析
            crew = self._get_crew()
            result = crew.kickoff(full_question)
            
            # 解析结果
            parsed_result = self._parse_crew_result(result, question)
            parsed_result["query_id"] = query_id
            parsed_result["execution_time"] = time.time() - start_time
            
            print(f"[AnalysisService] 分析完成，耗时: {parsed_result['execution_time']:.2f}秒")
            
            return parsed_result
            
        except Exception as e:
            print(f"[AnalysisService] 分析失败: {str(e)}")
            return {
                "query_id": query_id,
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def _parse_crew_result(self, result, question: str) -> Dict[str, Any]:
        """解析 Crew 执行结果"""
        print(f"[AnalysisService] 解析结果类型: {type(result)}")
        
        if isinstance(result, str):
            parsed = {
                "report": result,
                "data": self._extract_data_from_markdown(result),
                "insights": self._extract_insights_from_report(result),
                "sql": self._extract_sql_from_report(result)
            }
            print(f"[AnalysisService] 提取结果 - data: {len(parsed['data'])} 行, insights: {len(parsed['insights'])} 条, sql: {'有' if parsed['sql'] else '无'}")
            return parsed
        elif isinstance(result, dict):
            return {
                "report": result.get("report", ""),
                "data": result.get("data", []),
                "insights": result.get("insights", []),
                "sql": result.get("sql", "")
            }
        else:
            return {
                "report": str(result),
                "data": [],
                "insights": [],
                "sql": ""
            }
    
    def _extract_data_from_markdown(self, markdown: str) -> List[Dict[str, Any]]:
        """从 Markdown 中提取表格数据"""
        try:
            lines = markdown.split('\n')
            tables = []
            current_table = []
            in_table = False
            
            for line in lines:
                if '|' in line and not line.strip().startswith('|---'):
                    current_table.append(line)
                    in_table = True
                elif in_table and '|' not in line:
                    if current_table:
                        tables.append(self._parse_markdown_table(current_table))
                    current_table = []
                    in_table = False
            
            return tables[0] if tables else []
            
        except Exception as e:
            print(f"[AnalysisService] 提取表格失败: {e}")
            return []
    
    def _parse_markdown_table(self, lines: List[str]) -> List[Dict[str, Any]]:
        """解析 Markdown 表格"""
        if len(lines) < 2:
            return []
        
        header = [cell.strip() for cell in lines[0].strip('|').split('|')]
        
        data = []
        for line in lines[1:]:
            if line.strip().startswith('|---'):
                continue
            row = [cell.strip() for cell in line.strip('|').split('|')]
            if len(row) == len(header):
                data.append(dict(zip(header, row)))
        
        return data
    
    def _extract_insights_from_report(self, report: str) -> List[str]:
        """从报告中提取洞察"""
        insights = []
        lines = report.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ['洞察', '发现', '结论', '建议']):
                if line.strip() and not line.startswith('#'):
                    insights.append(line.strip('- ').strip())
        
        return insights[:5]
    
    def _extract_sql_from_report(self, report: str) -> str:
        """从报告中提取SQL"""
        try:
            if '```sql' in report:
                start = report.index('```sql') + 6
                end = report.index('```', start)
                return report[start:end].strip()
            elif 'SELECT' in report.upper():
                for line in report.split('\n'):
                    if 'SELECT' in line.upper():
                        return line.strip()
        except:
            pass
        
        return ""


# ============================================
# 存储服务
# ============================================

class StorageService:
    """数据存储服务"""
    
    def __init__(self):
        self.engine = None
        self.metadata = MetaData()
        self._init_engine()
        self._create_tables()
    
    def _init_engine(self):
        """初始化数据库"""
        try:
            from config import DB_CONFIG
            connection_string = (
                f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            )
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            print("[StorageService] 数据库连接成功")
        except Exception as e:
            print(f"[StorageService] 数据库连接失败: {e}")
    
    def _create_tables(self):
        """创建数据表"""
        # 查询历史表
        Table(
            'api_query_history', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('query_id', String(100), unique=True, nullable=False),
            Column('question', Text, nullable=False),
            Column('user_id', String(100)),
            Column('status', String(20)),
            Column('executed_sql', Text),
            Column('result_rows', Integer),
            Column('execution_time', Float),
            Column('created_at', DateTime, default=datetime.now),
            extend_existing=True
        )
        
        try:
            self.metadata.create_all(self.engine)
            print("[StorageService] 数据表创建成功")
        except Exception as e:
            print(f"[StorageService] 创建表失败: {e}")
    
    def check_connection(self) -> bool:
        """检查数据库连接"""
        if not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False
    
    def save_query_result(
        self,
        query_id: str,
        question: str,
        result: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """保存查询结果"""
        try:
            query_history = {
                'query_id': query_id,
                'question': question,
                'user_id': user_id,
                'status': result.get('status', 'unknown'),
                'executed_sql': result.get('sql', ''),
                'result_rows': len(result.get('data', [])),
                'execution_time': result.get('execution_time', 0)
            }
            
            df_history = pd.DataFrame([query_history])
            df_history.to_sql('api_query_history', self.engine, if_exists='append', index=False)
            
            print(f"[StorageService] 查询结果已保存: {query_id}")
            
        except Exception as e:
            print(f"[StorageService] 保存失败: {e}")
    
    def get_query_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[QueryHistory]:
        """获取查询历史"""
        try:
            query = "SELECT * FROM api_query_history"
            params = {}
            
            if user_id:
                query += " WHERE user_id = :user_id"
                params['user_id'] = user_id
            
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params['limit'] = limit
            params['offset'] = offset
            
            df = pd.read_sql(text(query), self.engine, params=params)
            
            return [QueryHistory(**row.to_dict()) for _, row in df.iterrows()]
            
        except Exception as e:
            print(f"[StorageService] 获取历史失败: {e}")
            return []
