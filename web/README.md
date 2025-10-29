# CrewAI 数据分析 - Web 前端

简约美观的 Web 前端界面，连接到 CrewAI 数据分析 API。

## 功能特性

### 智能问答页面 (index.html)

- 自然语言输入
- 示例问题快速选择
- 实时显示分析结果
- 业务洞察展示
- 数据表格可视化
- SQL 查询展示

### 查询历史页面 (history.html)

- 历史查询记录
- 统计信息展示（总查询数、平均时间、成功率）
- 查询详情查看
- 执行的 SQL 展示
- 时间戳显示

## 快速开始

### 1. 启动 API 服务

首先确保后端 API 已启动：

```bash
# Windows
start_api.bat

# Linux/Mac
bash start_api.sh
```

### 2. 启动 Web 服务器

**Windows:**

```bash
start_web.bat
```

**Linux/Mac:**

```bash
bash start_web.sh
```

**手动启动:**

```bash
cd web
python -m http.server 8080
```

### 3. 访问界面

在浏览器中打开：

```
http://localhost:8080
```

## 界面设计

### ChatGPT 风格

- **侧边栏导航**：深色侧边栏，简洁导航
- **对话式界面**：类似聊天应用的交互体验
- **卡片式设计**：清晰的内容区块
- **响应式布局**：适配移动端和桌面端

### 功能区域

1. **欢迎屏幕**：示例问题卡片，快速开始
2. **对话区域**：用户问题和 AI 回复
3. **输入框**：底部固定，支持多行输入
4. **历史记录**：独立页面，详细统计

## 技术栈

- **纯 HTML + CSS + JavaScript**
- **无框架依赖**
- **Fetch API** 调用后端
- **响应式设计**
- **现代 UI 风格**

## API 端点

前端调用以下 API 接口：

| 接口              | 方法 | 说明     |
| ----------------- | ---- | -------- |
| `/api/v1/analyze` | POST | 数据分析 |
| `/api/v1/history` | GET  | 查询历史 |
| `/health`         | GET  | 健康检查 |

## 使用说明

### 提问方式

1. **直接输入问题**

   ```
   哪个国家的客户消费最多？
   ```

2. **点击示例问题**

   - 选择预设的示例问题快速提问

3. **快捷键**
   - `Enter`：提交问题
   - `Shift + Enter`：换行

### 查看历史

1. 点击侧边栏「历史记录」
2. 可以查看：
   - 所有查询记录
   - 执行的 SQL
   - 查询时间和状态
   - 统计信息

## 配置说明

### 修改 API 地址

如果 API 不在 `localhost:8000`，请修改：

**app.js:**

```javascript
const API_BASE_URL = "http://your-api-host:8000";
```

**history.js:**

```javascript
const API_BASE_URL = "http://your-api-host:8000";
```

### 修改 Web 端口

```bash
# 默认 8080
python -m http.server 8080

# 自定义端口
python -m http.server 3000
```

## 自定义样式

所有样式在 `style.css` 中定义，可修改：

```css
:root {
  --bg-primary: #ffffff; /* 主背景色 */
  --accent-color: #10a37f; /* 强调色 */
  --sidebar-bg: #202123; /* 侧边栏背景 */
  --text-primary: #353740; /* 主文字色 */
}
```

## 响应式设计

- **桌面端**：侧边栏 + 主内容区
- **平板端**：自动调整布局
- **移动端**：隐藏侧边栏，全屏对话

## 注意事项

1. **CORS 配置**：API 已配置允许跨域访问
2. **浏览器兼容**：推荐使用现代浏览器（Chrome、Firefox、Edge）
3. **API 依赖**：前端依赖后端 API，请确保 API 服务已启动

## 安全提示

- 当前版本为演示版本，无身份验证
- 生产环境建议添加 JWT 认证
- 敏感数据请不要在问题中包含

## 文件说明

```
web/
├── index.html       # 主页（问答界面）
├── history.html     # 历史记录页面
├── style.css        # 全局样式
├── app.js          # 主页逻辑
├── history.js      # 历史页面逻辑
└── README.md       # 本文档
```

## 开发说明

### 添加新功能

1. **修改 HTML**：添加新的 DOM 元素
2. **更新 CSS**：添加样式规则
3. **编写 JS**：添加事件处理逻辑

### 调试技巧

1. 打开浏览器开发者工具（F12）
2. 查看 Console 输出
3. 检查 Network 请求
4. 使用 Elements 面板调整样式

---

**简约而不简单，专注核心功能！**
