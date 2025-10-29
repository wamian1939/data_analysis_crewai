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
            用户问题：{question}
            
            ⚠️ 重要：你必须从数据库中查询实际数据，不能凭空回答！
            
            你的任务（必须按顺序执行）：
            1. 首先，使用 get_database_schema() 查看数据库有哪些表和字段
            2. 然后，使用 nl2sql() 工具将问题转换为 SQL 查询
            3. 最后，使用 sql_query_md() 工具执行 SQL 查询
            4. 返回 Markdown 格式的**真实数据表格**
            
            ⛔ 禁止行为：
            - 不能不查询数据库就直接回答问题
            - 不能编造虚假数据
            - 不能给出没有数据支撑的通用建议
            
            如果问题涉及"销售"、"订单"、"员工"等：
            - 先用 get_csv_schema() 查看 CSV 文件是否有相关数据
            - 如果有，用 csv_query() 查询 CSV 数据
            - 如果没有，查询数据库
            
            如果问题涉及"客户"、"艺人"、"专辑"、"流派"：
            - 直接查询 MySQL 数据库
            
            必须返回：包含实际查询结果的 Markdown 表格
            """,
            agent=self.data_engineer,
            expected_output="包含真实数据的 Markdown 格式查询结果表格（不能是空表格或编造的数据）"
        )
        
        # 任务 2：业务洞察（BizAnalyst）
        task_analyze_insights = Task(
            description="""
            基于上一步的**真实数据表格**，提取业务洞察。
            
            ⚠️ 重要：你的分析必须完全基于上一步查询到的真实数据！
            
            你的任务：
            1. 仔细查看上一步返回的数据表格
            2. 使用 summarize_table 工具分析这个表格
            3. 识别数据中的 TOP 项、趋势和关键模式
            4. 提炼 2-3 条**有数据支撑**的业务洞察
            5. 如果需要，使用 calculate_kpi 工具计算 KPI
            
            ⛔ 禁止行为：
            - 不能凭空编造洞察
            - 不能说数据表格中没有的内容
            - 洞察必须引用具体的数据（数字、比例等）
            
            输出格式：
            - 每条洞察应该清晰、具体、引用真实数据
            - 例如："USA 客户消费 $1,234，占比 22%"（有具体数字）
            - 不要说泛泛的通用建议
            """,
            agent=self.biz_analyst,
            expected_output="2-3 条基于真实数据的关键业务洞察（必须包含具体数字）",
            context=[task_extract_data]  # 依赖第一个任务的输出
        )
        
        # 任务 3：生成报告（Reporter）
        task_generate_report = Task(
            description=f"""
            基于前两步的**真实数据和洞察**，生成一份完整的管理层报告。
            
            ⚠️ 重要：报告必须完全基于前两步的真实数据，不能添加任何编造的内容！
            
            报告结构（严格遵守）：
            # 数据分析报告
            
            ## 📋 分析问题
            {question}
            
            ## 📊 数据查询结果
            [完整插入第一步的数据表格 - 必须保留原始数据]
            
            ## 💡 关键业务洞察
            [完整插入第二步的洞察 - 必须包含具体数字]
            
            ## 🎯 建议与行动项
            基于以上**真实数据**和洞察，给出 2-3 条可操作的建议。
            建议必须针对数据中发现的具体问题，不能是泛泛而谈。
            
            ⛔ 禁止行为：
            - 不能删除或修改第一步的数据表格
            - 不能删除或修改第二步的洞察
            - 不能添加数据中没有的内容
            - 建议必须基于数据，不能凭空想象
            
            要求：
            - 使用清晰的 Markdown 格式
            - 保持数据的完整性和真实性
            - 语言简洁专业，面向管理层
            - 所有建议必须引用具体的数据发现
            """,
            agent=self.reporter,
            expected_output="基于真实数据的完整 Markdown 格式管理层报告（必须包含完整的数据表格和洞察）",
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

