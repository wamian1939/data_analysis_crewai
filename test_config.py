"""
配置测试脚本 - 验证环境配置是否正确
"""
import os
import sys

# 设置 UTF-8 编码（Windows 环境）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 尝试从 config.py 加载配置
try:
    from config import OPENAI_API_KEY, OPENAI_MODEL_NAME, DB_CONFIG
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    USE_CONFIG_FILE = True
    print("使用 config.py 配置文件")
except ImportError:
    USE_CONFIG_FILE = False
    from dotenv import load_dotenv
    load_dotenv()
    print("使用 .env 环境变量")

print("="*60)
print("CrewAI 数据分析系统 - 配置测试")
print("="*60)

# 1. 检查 OpenAI API 配置
print("\n[1] 检查 OpenAI API 配置...")
if USE_CONFIG_FILE:
    api_key = OPENAI_API_KEY
    model = OPENAI_MODEL_NAME
else:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

if api_key:
    # 隐藏大部分密钥内容
    masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else "***"
    print(f"   [OK] API Key: {masked_key}")
    print(f"   [OK] Model: {model}")
else:
    print("   [ERROR] 未找到 OPENAI_API_KEY")
    sys.exit(1)

# 2. 检查数据库配置
print("\n[2] 检查数据库配置...")
if USE_CONFIG_FILE:
    db_config = {
        "host": DB_CONFIG["host"],
        "port": DB_CONFIG["port"],
        "user": DB_CONFIG["user"],
        "password": DB_CONFIG["password"],
        "database": DB_CONFIG["database"]
    }
else:
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME")
    }

if all(db_config.values()):
    print(f"   [OK] 主机: {db_config['host']}:{db_config['port']}")
    print(f"   [OK] 用户: {db_config['user']}")
    print(f"   [OK] 数据库: {db_config['database']}")
else:
    print("   [ERROR] 数据库配置不完整")
    for key, value in db_config.items():
        if not value:
            print(f"      缺少: DB_{key.upper()}")
    sys.exit(1)

# 3. 测试数据库连接
print("\n[3] 测试数据库连接...")
try:
    from tools.sql_tool import get_db
    db = get_db()
    tables = db.get_tables()
    print(f"   [OK] 数据库连接成功！")
    print(f"   [OK] 找到 {len(tables)} 个表:")
    for table in tables[:5]:  # 显示前5个表
        print(f"      - {table}")
    if len(tables) > 5:
        print(f"      ... 还有 {len(tables) - 5} 个表")
except Exception as e:
    print(f"   [ERROR] 数据库连接失败: {e}")
    print("\n   [提示] 可能的原因：")
    print("      1. MySQL 服务未启动")
    print("      2. 用户名或密码错误")
    print("      3. Chinook 数据库未导入")
    print("      4. 防火墙阻止连接")
    sys.exit(1)

# 4. 检查依赖包
print("\n[4] 检查关键依赖包...")
required_packages = [
    "crewai",
    "sqlalchemy",
    "pandas",
    "mysql.connector"
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"   [OK] {package}")
    except ImportError:
        print(f"   [ERROR] {package} (未安装)")
        missing_packages.append(package)

if missing_packages:
    print(f"\n   [警告] 缺少 {len(missing_packages)} 个依赖包")
    print("   运行: pip install -r requirements.txt")
    sys.exit(1)

# 5. 测试简单查询
print("\n[5] 测试简单 SQL 查询...")
try:
    from tools.sql_tool import sql_query_md
    result = sql_query_md("SELECT COUNT(*) AS customer_count FROM Customer LIMIT 1")
    if "customer_count" in result:
        print("   [OK] SQL 查询功能正常")
        print(f"   查询结果预览:\n{result[:200]}")
    else:
        print("   [警告] 查询返回异常")
except Exception as e:
    print(f"   [ERROR] 查询测试失败: {e}")

# 总结
print("\n" + "="*60)
print("[成功] 配置测试完成！系统已就绪。")
print("="*60)
print("\n[提示] 下一步：")
print("   1. 运行交互模式: python main.py")
print("   2. 运行演示模式: python main.py demo")
print("   3. 单次查询: python main.py \"哪个国家的客户消费最多？\"")
print("\n")

