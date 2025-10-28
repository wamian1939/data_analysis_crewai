"""
Insight Tool - 数据洞察提取工具
从 Markdown 表格中提取关键业务洞察
"""
from crewai.tools import tool
import re
from typing import List


@tool("summarize_table")
def summarize_table(markdown_table: str) -> str:
    """
    从 Markdown 表格中提取业务洞察
    
    参数:
        markdown_table: Markdown 格式的表格数据
    
    返回:
        2-3 条关键业务洞察
    """
    try:
        # 解析 Markdown 表格
        lines = markdown_table.strip().split('\n')
        
        # 过滤掉分隔线和空行
        data_lines = [line for line in lines if line.strip() and '---' not in line]
        
        if len(data_lines) < 2:
            return "数据不足，无法生成洞察。"
        
        # 提取表头
        header = data_lines[0]
        columns = [col.strip() for col in header.split('|') if col.strip()]
        
        # 提取数据行
        data_rows = []
        for line in data_lines[1:]:
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            if row:
                data_rows.append(row)
        
        if not data_rows:
            return "未找到有效数据行。"
        
        # 生成洞察
        insights = []
        
        # 洞察1：总行数
        insights.append(f"📊 数据概览：共发现 {len(data_rows)} 条记录。")
        
        # 洞察2：识别 TOP 项（第一行通常是最重要的）
        if data_rows:
            first_row = data_rows[0]
            if len(first_row) >= 2:
                key_field = columns[0] if columns else "项目"
                value_field = columns[-1] if len(columns) > 1 else "值"
                insights.append(
                    f"🏆 TOP 1 {key_field}：{first_row[0]}，"
                    f"{value_field} 为 {first_row[-1]}。"
                )
        
        # 洞察3：数值型字段的分析
        numeric_insights = analyze_numeric_columns(columns, data_rows)
        if numeric_insights:
            insights.append(numeric_insights)
        
        # 洞察4：分布特征
        if len(data_rows) >= 3:
            distribution_insight = analyze_distribution(data_rows, columns)
            if distribution_insight:
                insights.append(distribution_insight)
        
        return "\n\n".join(insights[:3])  # 最多返回 3 条洞察
        
    except Exception as e:
        return f"分析失败: {str(e)}"


def analyze_numeric_columns(columns: List[str], data_rows: List[List[str]]) -> str:
    """分析数值型列的特征"""
    try:
        # 尝试找到包含"金额"、"数量"、"收入"等关键字的列
        numeric_keywords = ["金额", "收入", "数量", "total", "amount", "revenue", "count"]
        
        for i, col in enumerate(columns):
            col_lower = col.lower()
            if any(kw in col_lower for kw in numeric_keywords):
                # 提取该列的数值
                values = []
                for row in data_rows:
                    if i < len(row):
                        # 清理数值（移除逗号、货币符号等）
                        value_str = re.sub(r'[^\d.]', '', row[i])
                        if value_str:
                            try:
                                values.append(float(value_str))
                            except ValueError:
                                continue
                
                if len(values) >= 2:
                    total = sum(values)
                    top_value = values[0] if values else 0
                    top_percentage = (top_value / total * 100) if total > 0 else 0
                    
                    return (
                        f"💰 {col}分析：TOP 1 占总体的 {top_percentage:.1f}%，"
                        f"显示出{'显著的集中度' if top_percentage > 30 else '相对均衡的分布'}。"
                    )
        
        return ""
    except Exception:
        return ""


def analyze_distribution(data_rows: List[List[str]], columns: List[str]) -> str:
    """分析数据分布特征"""
    try:
        total_rows = len(data_rows)
        
        if total_rows >= 5:
            # 比较 TOP 3 与其他的差异
            return (
                f"📈 分布特征：前 3 名占据主导地位，"
                f"建议重点关注头部 {min(5, total_rows)} 个{columns[0] if columns else '项目'}。"
            )
        else:
            return f"📉 数据集较小，建议收集更多样本以获得更全面的洞察。"
    except Exception:
        return ""


@tool("calculate_kpi")
def calculate_kpi(metric_name: str, value1: float, value2: float = None) -> str:
    """
    计算常见的业务 KPI 指标
    
    参数:
        metric_name: KPI 指标名称（growth_rate, margin, average 等）
        value1: 第一个数值
        value2: 第二个数值（可选）
    
    返回:
        KPI 计算结果
    """
    try:
        if metric_name.lower() in ["growth", "growth_rate", "增长率"]:
            if value2 is None or value2 == 0:
                return "❌ 增长率计算需要两个非零数值（当前值和基准值）"
            growth_rate = ((value1 - value2) / value2) * 100
            trend = "增长" if growth_rate > 0 else "下降"
            return f"📊 增长率：{abs(growth_rate):.2f}% ({trend})"
        
        elif metric_name.lower() in ["margin", "利润率", "毛利率"]:
            if value2 is None or value2 == 0:
                return "❌ 利润率计算需要利润和收入两个数值"
            margin = (value1 / value2) * 100
            return f"💹 利润率：{margin:.2f}%"
        
        elif metric_name.lower() in ["average", "平均值"]:
            return f"📊 平均值：{value1:.2f}"
        
        else:
            return f"❓ 未知的 KPI 指标：{metric_name}"
            
    except Exception as e:
        return f"KPI 计算失败: {str(e)}"

