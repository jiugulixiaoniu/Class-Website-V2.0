function updateMembersTable(data) {
    const tbody = document.querySelector('.members-table tbody');
    // 检查数据是否为数组
    if (!Array.isArray(data)) {
        console.error('获取到的数据不是数组:', data);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px; color: var(--gray-color);">获取数据失败，请检查API返回格式</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(member => `
        <tr>
            <td>${member.id}</td>
            <td>${member.display_name}</td>
            <td>${getLevelName(member.level)}</td>
            <td>${member.last_login ? new Date(member.last_login).toLocaleString() : '从未登录'}</td>
            <td>${new Date(member.created_at).toLocaleString()}</td>
            <td><i class="status-icon ${member.is_online ? 'online' : 'offline'}"></i></td>
            <td><i class="status-icon ${member.is_banned ? 'banned' : ''}"></i></td>
            <td>
                <button class="btn-small edit-btn" onclick="openEditMember(${member.id})"><i class="fas fa-edit"></i></button>
                <button class="btn-small ban-btn" onclick="toggleBanMember(${member.id})"><i class="fas ${member.is_banned ? 'fa-unlock' : 'fa-ban'}"></i></button>
                <button class="btn-small delete-btn" onclick="deleteMember('${member.id}')"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}
const activityIcons = {
    'login': 'fas fa-sign-in-alt',
    'logout': 'fas fa-sign-out-alt',
    'add': 'fas fa-plus',
    'edit': 'fas fa-edit',
    'delete': 'fas fa-trash',
    'ban': 'fas fa-ban',
    'unban': 'fas fa-unlock',
    'register': 'fas fa-user-plus',
    'view': 'fas fa-eye',
    'error': 'fas fa-exclamation-circle',
    'default': 'fas fa-history'
};

// 活动类型颜色映射
const activityColors = {
    'login': '#4CAF50',
    'logout': '#F44336',
    'add': '#2196F3',
    'edit': '#FFC107',
    'delete': '#9C27B0',
    'ban': '#E91E63',
    'unban': '#009688',
    'register': '#3F51B5',
    'view': '#00BCD4',
    'error': '#FF5722',
    'default': '#607D8B'
};

// 活动类型文本映射
const activityTexts = {
    'login': '登录了系统',
    'logout': '登出了系统',
    'add': '添加了',
    'edit': '编辑了',
    'delete': '删除了',
    'ban': '封禁了',
    'unban': '解封了',
    'register': '注册了',
    'view': '查看了',
    'error': '发生了错误',
    'default': '执行了操作'
};
// 获取成员数据
async function fetchMembers() {
    try {
        const response = await fetch('http://localhost:5000/api/members');
        if (!response.ok) {
            throw new Error('请求失败');
        }
        const data = await response.json();
        updateMembersTable(data.users || data); // 兼容不同返回格式
    } catch (error) {
        console.error('获取成员数据失败:', error);
        showNotification('无法获取成员数据，请检查网络连接', 'error');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 页面切换功能
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href');
            showSection(sectionId);
        });
    });

    // 初始化搜索监听器
    initSearchListeners();

    // 获取成员数据
    fetchMembers();
});
// 获取等级名称
function getLevelName(level) {
    const levelMap = {
        1: '访客',
        2: '普通用户',
        3: '内容管理员',
        4: '系统管理员',
        5: '超级管理员',
        6: '开发者管理员'
    };
    return levelMap[level] || '未知';
}

// 初始化搜索功能
function initSearchListeners() {
    const searchInput = document.getElementById('memberSearch');
    const searchButton = document.getElementById('searchBtn');

    // 统一绑定搜索事件
    if (searchButton && searchInput) {
        // 点击搜索按钮
        searchButton.addEventListener('click', function() {
            fetchMembersWithFilter();
        });

        // 回车键触发
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                fetchMembersWithFilter();
            }
        });

        // 输入变化实时搜索（可选）
        searchInput.addEventListener('input', function() {
            fetchMembersWithFilter();
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 页面切换功能
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href');
            showSection(sectionId);
        });
    });

    // 初始化搜索监听器
    initSearchListeners();

    // 获取成员数据
    fetchMembers();
});

// 显示指定页面
function showSection(sectionId) {
    const contentSections = document.querySelectorAll('.content-section');
    contentSections.forEach(section => {
        section.classList.remove('active');
        if (section.id === sectionId.substring(1)) {
            section.classList.add('active');
        }
    });
}

// 打开编辑成员模态框
function openEditMember(memberId) {
    // 获取成员详情并填充到表单中
    fetchMemberDetails(memberId);
}

// 获取成员详情
async function fetchMemberDetails(memberId) {
    try {
        const response = await fetch(`http://localhost:5000/api/members/${memberId}`);
        if (!response.ok) {
            throw new Error('无法获取成员详情');
        }
        const member = await response.json();

        // 填充表单
        document.getElementById('editMemberId').value = member.id;
        document.getElementById('editUsername').value = member.username;
        document.getElementById('editDisplayName').value = member.display_name;
        document.getElementById('editPhone').value = member.phone;
        document.getElementById('editEmail').value = member.email;
        document.getElementById('editLevel').value = member.level;

        // 显示模态框
        document.getElementById('editMemberModal').classList.add('active');
    } catch (error) {
        console.error('获取成员详情失败:', error);
        showNotification('获取成员详情失败', 'error');
    }
}

// 切换成员封禁状态
function toggleBanMember(memberId) {
    // 切换封禁状态的逻辑
    console.log(`切换成员封禁状态，成员ID: ${memberId}`);
}


// 成员编辑功能
let editMemberModal = document.getElementById('editMemberModal');
let editMemberId = document.getElementById('editMemberId');
let editUsername = document.getElementById('editUsername');
let editDisplayName = document.getElementById('editDisplayName');
let editPhone = document.getElementById('editPhone');
let editEmail = document.getElementById('editEmail');
let editLevel = document.getElementById('editLevel');
let closeEditModal = document.querySelector('.close-modal');
let cancelEditButton = document.getElementById('cancelEditMember');
let saveEditButton = document.getElementById('saveEditMember');

// 关闭模态框
if (closeEditModal) {
    closeEditModal.addEventListener('click', function() {
        if (editMemberModal) {
            editMemberModal.classList.remove('active');
        }
    });
}

// 取消编辑
if (cancelEditButton) {
    cancelEditButton.addEventListener('click', function() {
        if (editMemberModal) {
            editMemberModal.classList.remove('active');
        }
    });
}

// 保存编辑
document.getElementById('saveEditMember').addEventListener('click', function() {
    const memberId = document.getElementById('editMemberId').value;
    const username = document.getElementById('editUsername').value;
    const display_name = document.getElementById('editDisplayName').value;
    const phone = document.getElementById('editPhone').value;
    const email = document.getElementById('editEmail').value;
    const level = document.getElementById('editLevel').value;

    fetch(`http://localhost:5000/api/members/${memberId}/edit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        },
        body: JSON.stringify({
            username: username,
            display_name: display_name,
            phone: phone,
            email: email,
            level: level
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('保存失败');
        }
        return response.json();
    })
    .then(data => {
        console.log('保存成功', data);
        fetchMembers();
        document.getElementById('editMemberModal').classList.remove('active');
        showNotification('成员信息保存成功', 'success');
    })
    .catch(error => {
        console.error('保存失败:', error);
        showNotification('保存成员信息失败', 'error');
    });
});

// 成员管理页面操作
const memberButtons = document.querySelectorAll('.members-table .btn-small');
memberButtons.forEach(button => {
    button.addEventListener('click', function() {
        const memberId = this.closest('tr').querySelector('td:first-child').textContent;
        const action = this.classList.contains('edit-btn') ? '编辑' :
                       this.classList.contains('ban-btn') ? '封禁' : '删除';
        alert(`您点击了 ${action} 成员 ID: ${memberId}`);
    });
});
function toggleBanMember(memberId) {
    fetch(`http://localhost:5000/api/members/${memberId}/ban`, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('操作失败');
        }
        return response.json();
    })
    .then(data => {
        console.log('操作成功', data);
        fetchMembers();
        showNotification(data.message, 'success');
    })
    .catch(error => {
        console.error('操作失败:', error);
        showNotification('操作失败', 'error');
    });
}

// 修改删除成员函数
function deleteMember(memberId) {
    if (!confirm(`确定删除成员 ${memberId} 吗？`)) return;

    fetch(`http://localhost:5000/api/members/${encodeURIComponent(memberId)}/delete`, {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            // 解析错误信息
            return response.json().then(err => Promise.reject(err))
        }
        return response.json()
    })
    .then(d => {
        showNotification(d.message, 'success');
        fetchMembers();
    })
    .catch(err => {
        console.error('删除失败:', err);
        showNotification(err.error || '删除失败，请检查控制台', 'error');
    });
}
// 文章管理页面操作
const articleButtons = document.querySelectorAll('.articles-table .btn-small');
articleButtons.forEach(button => {
    button.addEventListener('click', function() {
        const articleId = this.closest('tr').querySelector('td:first-child').textContent;
        const action = this.classList.contains('view-btn') ? '查看' :
                       this.classList.contains('edit-btn') ? '编辑' : '删除';
        alert(`您点击了 ${action} 文章 ID: ${articleId}`);
    });
});

// 文章标签切换
const tabButtons = document.querySelectorAll('.tab-btn');
tabButtons.forEach(button => {
    button.addEventListener('click', function() {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
    });
});

// 发布文章模态框
const publishButton = document.querySelector('[href="#articles"] + .section-actions .btn');
const publishModal = document.getElementById('publish-modal');
const closePublishModal = document.querySelector('.close-modal');
const cancelPublishButton = document.querySelector('.cancel-btn');

if (publishButton) {
    publishButton.addEventListener('click', function(e) {
        e.stopPropagation();
        publishModal.classList.add('active');
    });
}

[closePublishModal, cancelPublishButton].forEach(button => {
    button.addEventListener('click', function() {
        publishModal.classList.remove('active');
    });
});

// 点击模态框外部关闭
publishModal.addEventListener('click', function(e) {
    if (e.target === this) {
        this.classList.remove('active');
    }
});

// 初始化时钟功能
function updateClock() {
    const now = new Date();
    const year = String(now.getFullYear()).padStart(4, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    const second = String(now.getSeconds()).padStart(2, '0');

    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.textContent = `${year}年${month}月${day}日   ${hour}:${minute}:${second}`;
    }
}
async function fetchLogs() {
    try {
        const response = await fetch('http://localhost:5000/api/logs');
        if (!response.ok) {
            throw new Error('请求失败');
        }
        const data = await response.json();
        console.log('Received logs data:', data); // 新增日志输出
        updateLogsTable(data);
    } catch (error) {
        console.error('获取访问日志失败:', error);
        showNotification('无法获取访问日志，请检查网络连接', 'error');
    }
}
// 更新访问日志表格
function updateLogsTable(logs) {
    const tbody = document.querySelector('#logs-list');
    if (!tbody) {
        console.error('Error: Element with id "logs-list" not found in the DOM.');
        return;
    }

    if (!Array.isArray(logs)) {
        console.error('获取到的日志数据不是数组:', logs);
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 20px; color: var(--gray-color);">获取日志失败，请检查API返回格式</td></tr>';
        return;
    }

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 20px; color: var(--gray-color);">没有找到任何日志记录</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>${log.id}</td>
            <td>${log.operator_user_id}</td>
            <td>${log.operator_username}</td>
            <td>${log.user_id}</td>
            <td>${log.username}</td>
            <td>${log.action}</td>
            <td>${log.ip_address}</td>
            <td>${getBrowserName(log.browser)}</td>
            <td>${log.device_type}</td>
            <td>${new Date(log.access_time).toLocaleString()}</td>
            <td>${log.location}</td>
        </tr>
    `).join('');
}

function getBrowserName(userAgent) {
    if (!userAgent) return '未知';
    userAgent = userAgent.toLowerCase();
    if (userAgent.includes('edg')) return 'Microsoft Edge';
    if (userAgent.includes('chrome')) return 'Google Chrome';
    if (userAgent.includes('firefox')) return 'Mozilla Firefox';
    if (userAgent.includes('safari')) return 'Safari';
    if (userAgent.includes('opera')) return 'Opera';
    return '其他浏览器';
}
// 新增控制台数据获取函数
async function fetchDashboardStats() {
    try {
        // 修正API路径
        const response = await fetch('http://localhost:5000/api/stats');
        if (!response.ok) {
            throw new Error('获取统计信息失败');
        }
        const data = await response.json();

        // 修正字段名
        document.getElementById('onlineUsers').textContent = data.online_users;
        document.getElementById('registeredUsers').textContent = data.registered_users;
        document.getElementById('articleCount').textContent = data.article_count;
        document.getElementById('todayVisits').textContent = data.today_visits;
    } catch (error) {
        console.error('获取统计信息失败:', error);
        showNotification('无法获取控制台数据', 'error');
    }
}
async function renderVisitsChart() {
    try {
        const response = await fetch('http://localhost:5000/api/visits/weekly', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        });

        if (!response.ok) {
            throw new Error('获取访问量数据失败');
        }

        const data = await response.json();

        // 获取 canvas 元素
        const ctx = document.getElementById('visits-chart').getContext('2d');

        // 如果已存在图表实例，先销毁
        if (window.visitsChart) {
            window.visitsChart.destroy();
        }

        // 创建新图表
        window.visitsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: '每日访问量',
                    data: data.visits,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: `最近一周访问量: ${data.total} 次`,
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        padding: 10,
                        callbacks: {
                            label: function(context) {
                                return `访问量: ${context.parsed.y}`;
                            },
                            title: function(context) {
                                return context[0].label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: '访问次数'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '日期'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'nearest'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });

    } catch (error) {
        console.error('渲染访问量图表失败:', error);
        showNotification('无法加载访问量图表', 'error');
    } finally {
        if (loadingElement) loadingElement.style.display = 'none';
    }
}


// 获取最近活动数据
async function fetchRecentActivities() {
    try {
        const response = await fetch('http://localhost:5000/api/activities/recent', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        });

        if (!response.ok) {
            throw new Error('获取活动数据失败');
        }

        const activities = await response.json();
        renderActivities(activities);
    } catch (error) {
        console.error('获取最近活动失败:', error);
        showNotification('无法获取最近活动数据', 'error');
        // 显示错误状态
        document.getElementById('activity-list').innerHTML = `
            <div class="activity-item error">
                <div class="activity-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="activity-content">
                    <p>无法加载活动数据</p>
                </div>
            </div>
        `;
    }
}

// 渲染活动数据
function renderActivities(activities) {
    const container = document.getElementById('activity-list');

    if (!activities || activities.length === 0) {
        container.innerHTML = `
            <div class="activity-item">
                <div class="activity-icon"><i class="fas fa-info-circle"></i></div>
                <div class="activity-content">
                    <p>暂无活动记录</p>
                </div>
            </div>
        `;
        return;
    }

    let html = '';
    activities.forEach(activity => {
        // 从动作中提取类型（第一个单词）
        const actionType = activity.action.toLowerCase().split(' ')[0];

        // 获取对应的图标、颜色和文本
        const icon = activityIcons[actionType] || activityIcons['default'];
        const color = activityColors[actionType] || activityColors['default'];
        const text = activityTexts[actionType] || activityTexts['default'];

        // 格式化时间
        const formattedTime = formatTimeAgo(activity.access_time);

        // 创建活动项HTML
        html += `
            <div class="activity-item">
                <div class="activity-icon" style="background-color: ${color}">
                    <i class="${icon}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-header">
                        <span class="activity-user">${activity.operator_username}</span>
                        <span class="activity-time">${formattedTime}</span>
                    </div>
                    <p>
                        <span class="activity-action">${activity.action}</span>
                        ${activity.username !== activity.operator_username ? 
                          `<span class="activity-target">${activity.username}</span>` : ''}
                    </p>
                    <div class="activity-meta">
                        <span class="activity-ip">${activity.ip_address}</span>
                        <span class="activity-location">${activity.location || '未知位置'}</span>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// 格式化时间为"XX前"的格式
function formatTimeAgo(timestamp) {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffSeconds = Math.floor((now - activityTime) / 1000);

    if (diffSeconds < 60) {
        return `${diffSeconds}秒前`;
    }

    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) {
        return `${diffMinutes}分钟前`;
    }

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) {
        return `${diffHours}小时前`;
    }

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}天前`;
}
// 确保在DOM加载时调用
async function fetchArticles() {
    try {
        const response = await fetch('http://localhost:5000/api/articles');
        if (!response.ok) {
            throw new Error('请求失败');
        }
        const data = await response.json();
        updateArticlesTable(data);
    } catch (error) {
        console.error('获取文章数据失败:', error);
        showNotification('无法获取文章数据，请检查网络连接', 'error');
    }
}

function updateArticlesTable(articles) {
    const tbody = document.querySelector('#articles-list');
    tbody.innerHTML = articles.map(article => `
        <tr>
            <td>${article.id}</td>
            <td>${article.title}</td>
            <td>${article.author_name}</td>
            <td>${article.status}</td>
            <td>${new Date(article.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn-small edit-btn" onclick="editArticle(${article.id})"><i class="fas fa-edit"></i></button>
                <button class="btn-small delete-btn" onclick="deleteArticle(${article.id})"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

// 删除文章
function deleteArticle(articleId) {
    if (!confirm(`确定删除文章 ID: ${articleId} 吗？`)) return;

    fetch(`http://localhost:5000/api/articles/${articleId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('删除失败');
        }
        return response.json();
    })
    .then(data => {
        showNotification('文章已删除', 'success');
        fetchArticles();
    })
    .catch(error => {
        console.error('删除文章失败:', error);
        showNotification('删除文章失败', 'error');
    });
}

// 编辑文章
function editArticle(articleId) {
    // 这里应该实现编辑文章的逻辑
    // 可以打开一个模态框或重定向到编辑页面
    window.location.href = `article.html?edit=${articleId}`;
}
// 初始化时钟并每秒更新
updateClock();
setInterval(updateClock, 1000);