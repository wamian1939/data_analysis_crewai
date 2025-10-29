// API 配置
const API_BASE_URL = 'http://localhost:8000';

// 对话历史
let conversationHistory = [];

// DOM 元素
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const messagesContainer = document.getElementById('messagesContainer');
const welcomeScreen = document.getElementById('welcomeScreen');
const newChatBtn = document.getElementById('newChatBtn');
const conversationInfo = document.getElementById('conversationInfo');
const messageCount = document.getElementById('messageCount');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 发送按钮
    sendBtn.addEventListener('click', handleSend);
    
    // 输入框事件
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // 自动调整输入框高度
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
    
    // 示例卡片
    document.querySelectorAll('.example-card').forEach(card => {
        card.addEventListener('click', () => {
            const question = card.dataset.question;
            messageInput.value = question;
            handleSend();
        });
    });
    
    // 新对话按钮
    newChatBtn.addEventListener('click', startNewConversation);
    
    // 全局快捷键
    document.addEventListener('keydown', (e) => {
        // Ctrl+N: 新对话
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            startNewConversation();
        }
    });
    
    // 加载保存的对话（如果有）
    loadSavedConversation();
});

// 开始新对话
function startNewConversation() {
    conversationHistory = [];
    messagesContainer.innerHTML = '';
    welcomeScreen.style.display = 'flex';
    conversationInfo.style.display = 'none';
    messageInput.value = '';
    messageInput.focus();
    updateMessageCount();
    saveConversation();
}

// 更新消息计数
function updateMessageCount() {
    messageCount.textContent = conversationHistory.length;
    if (conversationHistory.length > 0) {
        conversationInfo.style.display = 'block';
    } else {
        conversationInfo.style.display = 'none';
    }
}

// 保存对话到本地存储
function saveConversation() {
    try {
        localStorage.setItem('crewai_conversation', JSON.stringify({
            history: conversationHistory,
            timestamp: new Date().toISOString()
        }));
    } catch (e) {
        console.warn('Failed to save conversation:', e);
    }
}

// 加载保存的对话
function loadSavedConversation() {
    try {
        const saved = localStorage.getItem('crewai_conversation');
        if (saved) {
            const data = JSON.parse(saved);
            // 只加载24小时内的对话
            const savedTime = new Date(data.timestamp);
            const now = new Date();
            const hoursDiff = (now - savedTime) / (1000 * 60 * 60);
            
            if (hoursDiff < 24 && data.history && data.history.length > 0) {
                conversationHistory = data.history;
                updateMessageCount();
                // 注意：这里不恢复UI显示，只恢复对话历史用于上下文
            }
        }
    } catch (e) {
        console.warn('Failed to load conversation:', e);
    }
}

// 发送消息
async function handleSend() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // 隐藏欢迎屏幕
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }
    
    // 显示用户消息
    addMessage('user', message);
    
    // 添加到对话历史
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // 清空输入框
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // 禁用发送按钮
    sendBtn.disabled = true;
    
    // 显示加载消息
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message,
                user_id: 'web_user',
                save_result: true,
                conversation_history: conversationHistory.slice(0, -1)  // 发送除了最新问题外的历史
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // 移除加载消息
        removeMessage(loadingId);
        
        // 显示回复
        addAssistantMessage(result);
        
        // 构建助手回复内容（简化版，用于上下文）
        let assistantContent = '';
        if (result.insights && result.insights.length > 0) {
            assistantContent = result.insights.join('\n');
        } else if (result.report) {
            assistantContent = result.report.substring(0, 500);  // 只保留前500字符
        } else {
            assistantContent = '已完成数据分析';
        }
        
        // 添加到对话历史
        conversationHistory.push({
            role: 'assistant',
            content: assistantContent
        });
        
        // 更新消息计数和保存
        updateMessageCount();
        saveConversation();
        
    } catch (error) {
        // 移除加载消息
        removeMessage(loadingId);
        
        // 显示错误
        addMessage('assistant', `抱歉，发生了错误：${error.message}\n\n请确保 API 服务已启动。`);
        
        // 移除刚才添加的用户消息（因为请求失败了）
        if (conversationHistory.length > 0 && conversationHistory[conversationHistory.length - 1].role === 'user') {
            conversationHistory.pop();
        }
    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// 添加消息
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'U' : 'AI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = content;
    
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

// 添加助手回复
function addAssistantMessage(result) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 调试输出
    console.log('Result data:', result);
    
    // 完整报告（如果没有结构化数据，显示原始报告）
    if (result.report && (!result.data || result.data.length === 0) && (!result.insights || result.insights.length === 0)) {
        const reportDiv = document.createElement('div');
        reportDiv.className = 'message-text';
        reportDiv.style.whiteSpace = 'pre-wrap';
        reportDiv.textContent = result.report;
        contentDiv.appendChild(reportDiv);
    }
    
    // 业务洞察
    if (result.insights && result.insights.length > 0) {
        const insightsDiv = document.createElement('div');
        insightsDiv.className = 'result-section';
        
        const header = document.createElement('div');
        header.className = 'result-header';
        header.textContent = '关键洞察';
        insightsDiv.appendChild(header);
        
        const insightsContent = document.createElement('div');
        insightsContent.className = 'result-insights';
        
        result.insights.forEach(insight => {
            const item = document.createElement('div');
            item.className = 'insight-item';
            item.textContent = insight;
            insightsContent.appendChild(item);
        });
        
        insightsDiv.appendChild(insightsContent);
        contentDiv.appendChild(insightsDiv);
    }
    
    // 数据表格
    if (result.data && result.data.length > 0) {
        const tableSection = document.createElement('div');
        tableSection.className = 'result-section';
        
        const header = document.createElement('div');
        header.className = 'result-header';
        header.textContent = '数据结果';
        tableSection.appendChild(header);
        
        const tableWrapper = document.createElement('div');
        tableWrapper.className = 'result-table';
        tableWrapper.innerHTML = createTable(result.data);
        
        tableSection.appendChild(tableWrapper);
        contentDiv.appendChild(tableSection);
    }
    
    // SQL 查询
    if (result.executed_sql) {
        const sqlSection = document.createElement('div');
        sqlSection.className = 'result-section';
        
        const header = document.createElement('div');
        header.className = 'result-header';
        header.textContent = 'SQL 查询';
        sqlSection.appendChild(header);
        
        const sqlPre = document.createElement('pre');
        sqlPre.className = 'result-sql';
        sqlPre.textContent = result.executed_sql;
        
        sqlSection.appendChild(sqlPre);
        contentDiv.appendChild(sqlSection);
    }
    
    // 元信息
    const metaDiv = document.createElement('div');
    metaDiv.className = 'result-meta';
    metaDiv.innerHTML = `
        <div class="meta-item">
            <span class="meta-label">查询ID:</span>
            <span class="meta-value">${result.query_id || '-'}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">执行时间:</span>
            <span class="meta-value">${result.execution_time ? result.execution_time.toFixed(2) + 's' : '-'}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">状态:</span>
            <span class="meta-value">${result.status || '-'}</span>
        </div>
    `;
    
    contentDiv.appendChild(metaDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// 添加加载消息
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'loading-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'AI';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-message';
    loadingDiv.innerHTML = `
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    `;
    
    contentDiv.appendChild(loadingDiv);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return 'loading-message';
}

// 移除消息
function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) {
        message.remove();
    }
}

// 创建表格
function createTable(data) {
    if (!data || data.length === 0) {
        return '<p>无数据</p>';
    }
    
    const columns = Object.keys(data[0]);
    
    let html = '<table class="data-table">';
    
    // 表头
    html += '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${escapeHtml(col)}</th>`;
    });
    html += '</tr></thead>';
    
    // 表体
    html += '<tbody>';
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            html += `<td>${escapeHtml(String(row[col] || '-'))}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    
    return html;
}

// 滚动到底部
function scrollToBottom() {
    const container = document.querySelector('.chat-container');
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 100);
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
