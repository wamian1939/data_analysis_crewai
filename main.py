"""
主入口文件 - 启动数据分析 Crew
支持命令行交互和批量问题分析
"""
import os
import sys
from crew import DataAnalysisCrew

# 尝试从 config.py 加载配置
try:
    from config import OPENAI_API_KEY, DB_CONFIG
    # 设置为环境变量，供 CrewAI 使用
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    USE_CONFIG_FILE = True
except ImportError:
    USE_CONFIG_FILE = False
    from dotenv import load_dotenv
    load_dotenv()


def save_report(report: str, filename: str = "report.md"):
    """
    保存报告到文件
    
    参数:
        report: 报告内容
        filename: 文件名
    """
    # 创建 report/output 目录
    output_dir = "report/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存报告
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"📄 报告已保存到: {filepath}")


def run_analysis(question: str, save: bool = True):
    """
    运行单个问题的分析
    
    参数:
        question: 业务问题
        save: 是否保存报告
    """
    try:
        # 创建并启动 Crew
        crew = DataAnalysisCrew()
        result = crew.kickoff(question)
        
        # 打印结果
        print("\n" + "="*60)
        print("📊 最终报告")
        print("="*60)
        print(result)
        
        # 保存报告
        if save:
            # 生成文件名（使用问题的前20个字符）
            safe_filename = "".join(c for c in question[:20] if c.isalnum() or c in (' ', '-', '_'))
            safe_filename = safe_filename.strip().replace(' ', '_') + ".md"
            save_report(str(result), safe_filename)
        
        return result
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def interactive_mode():
    """交互式模式"""
    print("\n" + "="*60)
    print("🎯 CrewAI 数据分析系统 - 交互模式")
    print("="*60)
    print("\n支持的问题类型：")
    print("  1. 哪个国家的客户消费最多？")
    print("  2. 收入最高的艺人TOP10？")
    print("  3. 平均每张发票金额是多少？")
    print("  4. 按月份汇总的销售趋势？")
    print("  5. 最受欢迎的音乐流派？")
    print("\n输入 'quit' 或 'exit' 退出\n")
    
    while True:
        try:
            question = input("💬 请输入您的问题: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not question:
                print("⚠️  问题不能为空，请重新输入。")
                continue
            
            # 运行分析
            run_analysis(question, save=True)
            print("\n" + "-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def batch_mode(questions: list[str]):
    """批量分析模式"""
    print(f"\n🔄 批量分析模式：共 {len(questions)} 个问题\n")
    
    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"📝 问题 {i}/{len(questions)}: {question}")
        print(f"{'='*60}")
        
        result = run_analysis(question, save=True)
        results.append({
            'question': question,
            'result': result,
            'success': result is not None
        })
    
    # 汇总结果
    print(f"\n\n{'='*60}")
    print("📈 批量分析完成")
    print(f"{'='*60}")
    success_count = sum(1 for r in results if r['success'])
    print(f"✅ 成功: {success_count}/{len(questions)}")
    print(f"❌ 失败: {len(questions) - success_count}/{len(questions)}")
    
    return results


def main():
    """主函数"""
    # 检查配置
    if USE_CONFIG_FILE:
        print("✓ 使用 config.py 配置文件")
        if not OPENAI_API_KEY:
            print("⚠️  警告: 未在 config.py 中设置 OPENAI_API_KEY")
            return
        if not all(DB_CONFIG.values()):
            print("⚠️  警告: 数据库配置不完整")
            return
    else:
        print("✓ 使用 .env 环境变量配置")
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  警告: 未设置 OPENAI_API_KEY")
            print("请在 .env 文件或 config.py 中配置您的 API 密钥")
            return
        
        if not os.getenv("DB_HOST"):
            print("⚠️  警告: 未设置数据库配置")
            print("请在 .env 文件或 config.py 中配置数据库连接信息")
            return
    
    # 默认示例问题
    DEMO_QUESTIONS = [
        "哪个国家的客户消费最多？",
        "收入最高的艺人TOP10？",
        "平均每张发票金额是多少？"
    ]
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            # 演示模式：运行预设问题
            print("🎬 演示模式")
            batch_mode(DEMO_QUESTIONS)
        
        elif command == "batch":
            # 批量模式：从文件读取问题
            if len(sys.argv) < 3:
                print("用法: python main.py batch <questions_file>")
                return
            
            filepath = sys.argv[2]
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    questions = [line.strip() for line in f if line.strip()]
                batch_mode(questions)
            except FileNotFoundError:
                print(f"❌ 文件未找到: {filepath}")
        
        elif command == "help":
            print_help()
        
        else:
            # 单个问题模式
            question = " ".join(sys.argv[1:])
            run_analysis(question, save=True)
    
    else:
        # 默认交互模式
        interactive_mode()


def print_help():
    """打印帮助信息"""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║          CrewAI 数据分析系统 - 使用说明                      ║
╚══════════════════════════════════════════════════════════════╝

📝 使用方式：

  1. 交互模式（默认）:
     python main.py
     
  2. 单问题模式:
     python main.py "哪个国家的客户消费最多？"
     
  3. 演示模式（运行预设问题）:
     python main.py demo
     
  4. 批量模式（从文件读取问题）:
     python main.py batch questions.txt
     
  5. 帮助信息:
     python main.py help

📊 支持的问题类型：
  • 国家/地区分析："哪个国家的客户消费最多？"
  • 艺人排名："收入最高的艺人TOP10？"
  • 统计指标："平均每张发票金额是多少？"
  • 趋势分析："按月份汇总的销售趋势？"
  • 流派分析："最受欢迎的音乐流派？"

⚙️  环境配置：
  请确保 .env 文件包含以下配置：
  • OPENAI_API_KEY: OpenAI API 密钥
  • DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME: 数据库配置
    """
    print(help_text)


if __name__ == "__main__":
    main()

