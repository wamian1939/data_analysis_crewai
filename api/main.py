"""
FastAPI 主应用 - 精简版
只保留核心的问答和可视化功能
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crew import DataAnalysisCrew
from api.models import QueryRequest, QueryResponse, QueryHistory, HealthCheck
from api.services import AnalysisService, StorageService

# 创建 FastAPI 应用
app = FastAPI(
    title="CrewAI Data Analysis API",
    description="智能数据分析系统 - 自然语言查询 + Power BI 集成",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
analysis_service = AnalysisService()
storage_service = StorageService()


# ============================================
# 健康检查
# ============================================

@app.get("/", response_model=HealthCheck)
async def root():
    """API 根路径"""
    return HealthCheck(
        status="healthy",
        message="CrewAI Data Analysis API is running",
        version="1.0.0",
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查"""
    db_status = storage_service.check_connection()
    
    return HealthCheck(
        status="healthy" if db_status else "unhealthy",
        message="All systems operational" if db_status else "Database connection failed",
        version="1.0.0",
        timestamp=datetime.now()
    )


# ============================================
# 核心功能
# ============================================

@app.post("/api/v1/analyze", response_model=QueryResponse)
async def analyze_question(
    request: QueryRequest,
    background_tasks: BackgroundTasks
):
    """
    数据分析接口 - 向智能体提问
    
    示例:
        POST /api/v1/analyze
        {
            "question": "哪个国家的客户消费最多？",
            "user_id": "user_001",
            "save_result": true
        }
    """
    try:
        print(f"[API] 收到分析请求: {request.question}")
        
        # 转换对话历史格式
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # 执行分析
        result = await analysis_service.analyze(request.question, conversation_history)
        
        # 构建响应
        response = QueryResponse(
            query_id=result.get("query_id"),
            question=request.question,
            status="success",
            data=result.get("data"),
            insights=result.get("insights"),
            report=result.get("report"),
            executed_sql=result.get("sql"),
            execution_time=result.get("execution_time"),
            timestamp=datetime.now()
        )
        
        # 异步保存到数据库
        if request.save_result:
            background_tasks.add_task(
                storage_service.save_query_result,
                query_id=response.query_id,
                question=request.question,
                result=result,
                user_id=request.user_id
            )
        
        return response
        
    except Exception as e:
        print(f"[API] 分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.get("/api/v1/history")
async def get_query_history(
    user_id: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """
    查询历史记录 - 供 Power BI 连接使用
    
    参数:
        user_id: 用户ID（可选）
        limit: 返回数量（默认50）
        skip: 偏移量（用于分页）
    
    示例:
        GET /api/v1/history?limit=100
    
    Power BI 连接方式:
        获取数据 → Web → 输入: http://localhost:8000/api/v1/history?limit=100
    """
    try:
        history = storage_service.get_query_history(
            user_id=user_id,
            limit=limit,
            offset=skip
        )
        
        # 转换为字典列表（Power BI 友好格式）
        return [
            {
                "query_id": h.query_id,
                "question": h.question,
                "user_id": h.user_id,
                "status": h.status,
                "executed_sql": h.executed_sql,
                "result_rows": h.result_rows,
                "execution_time": h.execution_time,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


# ============================================
# 启动服务
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("CrewAI Data Analysis API Starting...")
    print("=" * 60)
    print("API Docs: http://localhost:8000/docs")
    print("Analyze API: POST http://localhost:8000/api/v1/analyze")
    print("History API: GET http://localhost:8000/api/v1/history")
    print("=" * 60)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
