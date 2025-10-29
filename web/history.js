// API 配置
const API_BASE_URL = 'http://localhost:8000';

// DOM 元素
const historyList = document.getElementById('historyList');
const emptyState = document.getElementById('emptyState');
const refreshBtn = document.getElementById('refreshBtn');
const limitSelect = document.getElementById('limitSelect');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    
    refreshBtn.addEventListener('click', loadHistory);
    limitSelect.addEventListener('change', loadHistory);
});

// 加载历史记录
async function loadHistory() {
    // 显示加载状态
    historyList.innerHTML = `
        <div class="loading-container">
            <div class="spinner"></div>
            <p>加载中...</p>
        </div>
    `;
    emptyState.style.display = 'none';
    
    try {
        const limit = limitSelect.value;
        const response = await fetch(`${API_BASE_URL}/api/v1/history?limit=${limit}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.length === 0) {
            historyList.innerHTML = '';
            emptyState.style.display = 'block';
        } else {
            displayHistory(data);
            displayStats(data);
        }
        
    } catch (error) {
        historyList.innerHTML = `
            <div class="error-card">
                <h3>加载失败</h3>
                <p>${escapeHtml(error.message)}</p>
                <p>请确保 API 服务已启动 (python api/main.py)</p>
            </div>
        `;
    }
}

// 显示历史记录
function displayHistory(data) {
    historyList.innerHTML = data.map(item => `
        <div class="history-item">
            <div class="history-question">${escapeHtml(item.question)}</div>
            <div class="history-meta">
                <div class="history-meta-item">
                    <span>ID:</span>
                    <span>${escapeHtml(item.query_id)}</span>
                </div>
                <div class="history-meta-item">
                    <span>用户:</span>
                    <span>${escapeHtml(item.user_id || 'anonymous')}</span>
                </div>
                <div class="history-meta-item">
                    <span>数据:</span>
                    <span>${item.result_rows || 0} 行</span>
                </div>
                <div class="history-meta-item">
                    <span>时间:</span>
                    <span>${item.execution_time ? item.execution_time.toFixed(2) + 's' : '-'}</span>
                </div>
                <div class="history-meta-item">
                    <span>创建:</span>
                    <span>${formatDate(item.created_at)}</span>
                </div>
                <div class="history-meta-item">
                    <span>状态:</span>
                    <span style="color: ${item.status === 'success' ? 'var(--accent-color)' : '#f44336'}">${item.status}</span>
                </div>
            </div>
            ${item.executed_sql ? `
                <div class="history-sql">${escapeHtml(item.executed_sql)}</div>
            ` : ''}
        </div>
    `).join('');
}

// 显示统计信息
function displayStats(data) {
    // 总查询数
    document.getElementById('totalQueries').textContent = data.length;
    
    // 平均时间
    const totalTime = data.reduce((sum, item) => sum + (item.execution_time || 0), 0);
    const avgTime = data.length > 0 ? (totalTime / data.length).toFixed(2) : 0;
    document.getElementById('avgTime').textContent = `${avgTime}s`;
    
    // 成功率
    const successCount = data.filter(item => item.status === 'success').length;
    const successRate = data.length > 0 ? ((successCount / data.length) * 100).toFixed(1) : 0;
    document.getElementById('successRate').textContent = `${successRate}%`;
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // 1分钟内
    if (diff < 60000) {
        return '刚刚';
    }
    
    // 1小时内
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} 分钟前`;
    }
    
    // 1天内
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} 小时前`;
    }
    
    // 7天内
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} 天前`;
    }
    
    // 超过7天，显示具体日期
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
