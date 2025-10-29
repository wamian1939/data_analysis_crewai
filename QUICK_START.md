# ⚡ 快速启动指南

只需 **3 步**，开始使用 CrewAI 智能数据分析系统！

## 📋 准备工作

1. **Python 3.8+** 已安装
2. **MySQL** 数据库已安装并运行
3. **OpenAI API Key** 已准备好

## 🚀 三步启动

### 第 1 步：安装依赖

```bash
pip install -r requirements.txt
```

### 第 2 步：配置系统

创建 `config.py` 文件：

```python
# OpenAI API 配置
OPENAI_API_KEY = "sk-your-openai-api-key"
OPENAI_MODEL_NAME = "gpt-4o-mini"

# MySQL 数据库配置
DB_CONFIG = {
    "user": "root",
    "password": "your_password",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "chinook",  # 你的数据库名
}
```

### 第 3 步：启动服务

#### Windows 用户

```batch
:: 启动 API 后端
start_api.bat

:: 启动 Web 前端（新窗口）
start_web.bat
```

#### Linux/Mac 用户

```bash
# 启动 API 后端
bash start_api.sh &

# 启动 Web 前端
bash start_web.sh
```

## 🎉 开始使用

### 访问 Web 界面

在浏览器中打开：**http://localhost:8080**

### 试试这些问题

- "哪个国家的客户消费最多？"
- "收入最高的艺人 TOP 10？"
- "最受欢迎的音乐流派是什么？"

## 📊 Power BI 集成

### 生成示例数据

```bash
python generate_powerbi_data.py
```

### 在 Power BI 中连接

1. 打开 **Power BI Desktop**
2. **获取数据** → **Web**
3. 输入 URL：`http://localhost:8000/api/v1/history`
4. 点击「确定」加载数据

## 🔧 常见问题

### 问题 1：API 启动失败

**检查：**

- MySQL 是否运行？
- `config.py` 配置是否正确？
- 端口 8000 是否被占用？

**解决：**

```bash
# 手动启动查看详细错误
python api/main.py
```

### 问题 2：Web 界面无法连接

**检查：**

- API 服务是否已启动？
- 访问 http://localhost:8000/health 检查 API 状态

**解决：**

```bash
# 先启动 API
python api/main.py

# 再启动 Web（新终端）
cd web
python -m http.server 8080
```

### 问题 3：数据库连接失败

**检查：**

- 数据库名称是否正确？
- 用户名和密码是否正确？
- MySQL 服务是否运行？

**解决：**

```bash
# 测试数据库连接
mysql -u root -p -e "SHOW DATABASES;"
```

### 问题 4：OpenAI API 错误

**检查：**

- API Key 是否正确？
- 账户是否有余额？
- 网络连接是否正常？

## 📖 更多文档

- **详细文档**：[README.md](README.md)
- **Web 前端**：[web/README.md](web/README.md)
- **API 文档**：http://localhost:8000/docs

## 🎯 使用流程图

```
┌─────────────────┐
│  1. 安装依赖    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 配置系统    │
│  (config.py)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 启动服务    │
│  API + Web      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 使用系统    │
│  提问 / 可视化  │
└─────────────────┘
```

## 💡 使用建议

### 最佳实践

1. **问题清晰**：问题越具体，结果越准确

   - ✅ "2023 年销售额最高的 5 个国家"
   - ❌ "销售情况"

2. **数据范围**：适当限制数据量

   - ✅ "TOP 10"、"最近一年"
   - ❌ "所有数据"

3. **查看历史**：在历史记录中查看之前的分析，避免重复查询

### 性能优化

- 首次查询会较慢（需要生成 SQL）
- 相似问题可以重复利用之前的结果
- 复杂查询可能需要 30-60 秒

## 🎨 界面预览

### 问答界面

- 渐变背景设计
- 简约卡片布局
- 实时结果展示

### 历史记录

- 查询统计信息
- SQL 语句展示
- 时间线追踪

---

**🎉 恭喜！你已经掌握了基本使用方法！**

有问题？查看 [README.md](README.md) 获取更多帮助。
