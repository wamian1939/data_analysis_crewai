"""
Crew 编排层 - 定义多 Agent 任务流程
协调 DataEngineer、BizAnalyst 和 Reporter 完成数据分析任务
"""
from crewai import Crew, Task, Process
from agents.data_engineer import create_data_engineer
from agents.biz_analyst import create_biz_analyst
from agents.reporter import create_reporter


class DataAnalysisCrew:
    """数据分析 Crew - 协调多个 Agent 完成分析任务"""
    
    def __init__(self):
        """初始化 Agents"""
        self.data_engineer = create_data_engineer()
        self.biz_analyst = create_biz_analyst()
        self.reporter = create_reporter()
    
    def create_tasks(self, question: str) -> list[Task]:
        """
        创建任务流程
        
        参数:
            question: 用户的业务问题
        
        返回:
            任务列表
        """
        # 任务 1：数据提取（DataEngineer）
        task_extract_data = Task(
            description=f"""
            分析用户问题：{question}
            
            你的任务：
            1. 使用 nl2sql 工具将问题转换为 SQL 查询
            2. 使用 sql_query_md 工具执行查询
            3. 返回 Markdown 格式的数据表格
            
            注意：
            - 只使用 SELECT 查询
            - 确保查询准确匹配用户需求
            - 如果不确定表结构，使用 get_database_schema 工具查看
            """,
            agent=self.data_engineer,
            expected_output="Markdown 格式的查询结果表格"
        )
        
        # 任务 2：业务洞察（BizAnalyst）
        task_analyze_insights = Task(
            description="""
            基于上一步的数据表格，提取业务洞察。
            
            你的任务：
            1. 使用 summarize_table 工具分析数据表格
            2. 识别 TOP 项、趋势和关键模式
            3. 提炼 2-3 条最有价值的业务洞察
            4. 如果需要，使用 calculate_kpi 工具计算 KPI
            
            输出格式：
            - 每条洞察应该清晰、具体、有业务价值
            - 使用表情符号增强可读性（📊 💰 🏆 等）
            """,
            agent=self.biz_analyst,
            expected_output="2-3 条关键业务洞察",
            context=[task_extract_data]  # 依赖第一个任务的输出
        )
        
        # 任务 3：生成报告（Reporter）
        task_generate_report = Task(
            description=f"""
            基于前两步的数据和洞察，生成一份完整的管理层报告。
            
            报告结构：
            # 数据分析报告
            
            ## 📋 分析问题
            {question}
            
            ## 📊 数据查询结果
            [插入第一步的数据表格]
            
            ## 💡 关键业务洞察
            [插入第二步的洞察]
            
            ## 🎯 建议与行动项
            基于以上数据和洞察，给出 2-3 条可操作的建议。
            
            要求：
            - 使用清晰的 Markdown 格式
            - 重点信息使用加粗或表情符号突出
            - 语言简洁专业，面向管理层
            - 避免技术术语
            """,
            agent=self.reporter,
            expected_output="完整的 Markdown 格式管理层报告",
            context=[task_extract_data, task_analyze_insights]  # 依赖前两个任务
        )
        
        return [task_extract_data, task_analyze_insights, task_generate_report]
    
    def kickoff(self, question: str) -> str:
        """
        启动分析流程
        
        参数:
            question: 用户的业务问题
        
        返回:
            最终的分析报告
        """
        print(f"\n{'='*60}")
        print(f"🚀 启动数据分析任务")
        print(f"📝 问题: {question}")
        print(f"{'='*60}\n")
        
        # 创建任务
        tasks = self.create_tasks(question)
        
        # 创建 Crew
        crew = Crew(
            agents=[self.data_engineer, self.biz_analyst, self.reporter],
            tasks=tasks,
            process=Process.sequential,  # 顺序执行
            verbose=True
        )
        
        # 执行任务
        result = crew.kickoff()
        
        print(f"\n{'='*60}")
        print(f"✅ 分析完成！")
        print(f"{'='*60}\n")
        
        return result

