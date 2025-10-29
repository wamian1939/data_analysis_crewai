"""
API 数据模型 - 精简版
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QueryStatus(str, Enum):
    """查询状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


# ============================================
# 请求模型
# ============================================

class ConversationMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., description="角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class QueryRequest(BaseModel):
    """分析请求"""
    question: str = Field(..., min_length=1, max_length=500, description="自然语言问题")
    user_id: Optional[str] = Field(None, description="用户ID")
    save_result: bool = Field(True, description="是否保存结果")
    conversation_history: Optional[List[ConversationMessage]] = Field(
        None, 
        description="对话历史（用于连续对话）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "哪个国家的客户消费最多？",
                "user_id": "user_001",
                "save_result": True,
                "conversation_history": []
            }
        }


# ============================================
# 响应模型
# ============================================

class QueryResponse(BaseModel):
    """分析响应"""
    query_id: str = Field(..., description="查询ID")
    question: str = Field(..., description="用户问题")
    status: QueryStatus = Field(..., description="查询状态")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="查询结果")
    insights: Optional[List[str]] = Field(None, description="业务洞察")
    report: Optional[str] = Field(None, description="完整报告")
    executed_sql: Optional[str] = Field(None, description="执行的SQL")
    execution_time: Optional[float] = Field(None, description="执行时间(秒)")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class QueryHistory(BaseModel):
    """查询历史"""
    query_id: str
    question: str
    user_id: Optional[str] = None
    status: QueryStatus
    executed_sql: Optional[str] = None
    result_rows: Optional[int] = None
    execution_time: Optional[float] = None
    created_at: datetime


class HealthCheck(BaseModel):
    """健康检查"""
    status: str
    message: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
