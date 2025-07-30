// 显示通知
function showNotification(message, type = 'success') {
    // 创建通知容器
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    document.body.appendChild(notificationContainer);

    // 创建通知内容
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${type === 'success' ? 'fa-check' : 'fa-times'}"></i>
        </div>
        <div class="notification-content">
            ${message}
        </div>
        <div class="notification-progress-bar"></div>
    `;
    notificationContainer.appendChild(notification);

    // 添加动画
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // 自动关闭通知
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notificationContainer.remove();
        }, 500);
    }, 3000);
}

// 初始化通知样式
function initNotificationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .recent-activities {
            background-color: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            padding: 20px;
            margin-top: 25px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .section-header h3 {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin: 0;
        }
        
        .refresh-btn {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 5px 12px;
            font-size: 13px;
            color: #6c757d;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .refresh-btn:hover {
            background: #e9ecef;
            color: #495057;
        }
        
        .activity-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .activity-item {
            display: flex;
            align-items: flex-start;
            padding: 15px;
            border-radius: 10px;
            background: #f8f9fa;
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .activity-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        
        .activity-item.loading {
            justify-content: center;
            align-items: center;
            min-height: 100px;
        }
        
        .activity-item.error {
            background: #fff8f8;
            border-left: 4px solid #ff6b6b;
        }
        
        .activity-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            flex-shrink: 0;
            margin-right: 15px;
        }
        
        .activity-content {
            flex: 1;
        }
        
        .activity-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .activity-user {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .activity-time {
            font-size: 12px;
            color: #6c757d;
        }
        
        .activity-content p {
            margin: 0;
            font-size: 14px;
            color: #495057;
            line-height: 1.5;
        }
        
        .activity-action {
            font-weight: 500;
        }
        
        .activity-target {
            background: #e3f2fd;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: 5px;
            font-weight: 500;
        }
        
        .activity-meta {
            display: flex;
            gap: 15px;
            margin-top: 8px;
            font-size: 12px;
            color: #6c757d;
        }
        
        .activity-ip, .activity-location {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .activity-ip::before {
            content: "🌐";
            font-size: 14px;
        }
        
        .activity-location::before {
            content: "📍";
            font-size: 14px;
        }
        /* 通知容器 */
        .notification-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            width: 350px;
        }

        /* 通知 */
        .notification {
            background: linear-gradient(135deg, #2b5876, #4e4376);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            color: white;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            transform: translateX(150%);
            transition: transform 0.3s ease-out;
            position: relative;
            overflow: hidden;
        }

        .notification.success {
            background: linear-gradient(135deg, #4CAF50, #2E7D32);
        }

        .notification.error {
            background: linear-gradient(135deg, #F44336, #D32F2F);
        }

        /* 通知图标 */
        .notification-icon {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .notification.success .notification-icon i {
            color: rgba(255, 255, 255, 0.9);
        }

        .notification.error .notification-icon i {
            color: rgba(255, 255, 255, 0.9);
        }

        /* 通知内容 */
        .notification-content {
            margin-bottom: 15px;
            font-weight: 500;
        }

        /* 通知进度条 */
        .notification-progress-bar {
            height: 3px;
            background: rgba(255, 255, 255, 0.3);
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            transform-origin: left;
            transform: scaleX(0);
            transition: transform 3s linear;
        }

        .notification.show .notification-progress-bar {
            transform: scaleX(1);
        }

        /* 显示动画 */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateX(150%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .notification.show {
            animation: fadeIn 0.3s forwards;
        }
    `;
    document.head.appendChild(style);
}

// 显示加载提示框
function showLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <span>加载中...</span>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
}

// 隐藏加载提示框
function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// 初始化加载样式
function initLoadingStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* 加载提示框 */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .loading-spinner {
            text-align: center;
            color: var(--primary-color);
        }

        .loading-spinner i {
            font-size: 3rem;
            margin-bottom: 20px;
        }
    `;
    document.head.appendChild(style);
}

// 为排序按钮添加事件监听器
function initSortingListeners() {
    const sortButtons = document.querySelectorAll('[data-sort]');
    sortButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sortField = this.getAttribute('data-sort');
            const currentOrder = this.getAttribute('data-order') || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

            // 更新按钮状态
            sortButtons.forEach(btn => {
                btn.classList.remove('sort-asc', 'sort-desc');
                btn.setAttribute('data-order', 'asc');
            });

            this.setAttribute('data-order', newOrder);
            this.classList.add(newOrder === 'asc' ? 'sort-asc' : 'sort-desc');

            // 触发排序操作
            fetchMembersWithFilter();
        });
    });
}

// 初始化过滤事件监听器
function initFilterListeners() {
    const filterSelects = document.querySelectorAll('.filter-group select');
    const searchInput = document.getElementById('memberSearch1');
    const searchButton = document.getElementById('searchBtn');
    const lastLoginStart = document.getElementById('lastLoginStart');
    const lastLoginEnd = document.getElementById('lastLoginEnd');
    const createdStart = document.getElementById('createdStart');
    const createdEnd = document.getElementById('createdEnd');
    const pageSizeSelect = document.getElementById('pageSizeSelect');

    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            fetchMembersWithFilter();
        });
    });

    searchButton.addEventListener('click', function() {
        fetchMembersWithFilter();
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchMembersWithFilter();
        }
    });

    lastLoginStart.addEventListener('change', fetchMembersWithFilter);
    lastLoginEnd.addEventListener('change', fetchMembersWithFilter);
    createdStart.addEventListener('change', fetchMembersWithFilter);
    createdEnd.addEventListener('change', fetchMembersWithFilter);
    pageSizeSelect.addEventListener('change', fetchMembersWithFilter);
}

// 初始化分页事件监听器
function initPaginationListeners() {
    const pageButtons = document.querySelectorAll('.pagination .page-btn:not(.disabled)');
    pageButtons.forEach(button => {
        button.addEventListener('click', function() {
            pageButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            fetchMembersWithFilter();
        });
    });
}
document.addEventListener('DOMContentLoaded', function() {
    fetchDashboardStats(); // 立即更新一次
    setInterval(fetchDashboardStats, 60000); // 每分钟更新一次
});
function updateMembersTableWithSearch(data) {
    const tbody = document.querySelector('.members-table tbody');
    if (!Array.isArray(data)) {
        console.error('获取到的数据不是数组:', data);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px; color: var(--gray-color);">获取数据失败，请检查API返回格式</td></tr>';
        return;
    }
    if (data.length === 0) {
        // 如果没有搜索结果，显示提示信息
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 20px; color: var(--gray-color);">
                    <i class="fas fa-info-circle" style="margin-right: 10px; color: var(--primary-color);"></i>
                    <span>没有找到匹配的成员</span>
                </td>
            </tr>
        `;
    } else {
        // 否则，显示搜索结果
        updateMembersTable(data);
    }
}
document.addEventListener('DOMContentLoaded', function() {
    // ...其他初始化代码...

    // 初始化控制台图表
    if (document.getElementById('visits-chart')) {
        renderVisitsChart();
    }

    // 当切换到控制台页面时刷新图表
    document.querySelector('[href="#dashboard"]').addEventListener('click', function() {
        if (document.getElementById('visits-chart')) {
            renderVisitsChart();
        }
    });
});

function initChartAutoRefresh() {
    // 每10分钟刷新一次数据
    setInterval(() => {
        if (document.querySelector('#dashboard.active') && document.getElementById('visits-chart')) {
            renderVisitsChart();
        }
    }, 600000); // 10分钟
}

// 在DOMContentLoaded中调用
document.addEventListener('DOMContentLoaded', function() {
    // ...其他代码...
    initChartAutoRefresh();
});
// 封装 fetchMembers 函数，添加筛选和排序功能
async function fetchMembersWithFilter() {
    try {
        showLoading(); // 显示加载提示框

        // 获取筛选条件
        const level = document.getElementById('levelFilter')?.value || '';
        const status = document.getElementById('statusFilter')?.value || '';
        const searchQuery = document.getElementById('memberSearch1')?.value || '';
        const lastLoginStart = document.getElementById('lastLoginStart')?.value || '';
        const lastLoginEnd = document.getElementById('lastLoginEnd')?.value || '';
        const createdStart = document.getElementById('createdStart')?.value || '';
        const createdEnd = document.getElementById('createdEnd')?.value || '';
        const pageSize = document.getElementById('pageSizeSelect')?.value || 30;
        const currentPage = document.querySelector('.pagination .page-btn.active')?.textContent || 1;

        // 获取排序条件
        const sortButton = document.querySelector('[data-sort].sort-asc, [data-sort].sort-desc');
        const sortField = sortButton?.getAttribute('data-sort') || 'id';
        const sortOrder = sortButton?.classList.contains('sort-asc') ? 'asc' : 'desc';

        // 构建查询参数
        const queryParams = new URLSearchParams({
            level: level,
            status: status,
            search: searchQuery,  // 确保参数名与后端API一致
            last_login_start: lastLoginStart,
            last_login_end: lastLoginEnd,
            created_start: createdStart,
            created_end: createdEnd,
            page: currentPage,
            page_size: pageSize,
            sort_by: sortField,    // 添加排序参数
            sort_order: sortOrder  // 添加排序方向
        });


        // 发送请求
        const response = await fetch(`http://localhost:5000/api/members?${queryParams.toString()}`);
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }
        const data = await response.json();

        // 处理响应数据
        updateMembersTableWithSearch(data.users || data); // 兼容不同返回格式
    } catch (error) {
        console.error('获取成员数据失败:', error);
        showNotification('无法获取成员数据，请检查网络连接', 'error');
    } finally {
        hideLoading(); // 隐藏加载提示框
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initNotificationStyles();
    initLoadingStyles();
    initSortingListeners();
    initFilterListeners();
    initPaginationListeners();
    fetchLogs();

    const refreshButton = document.getElementById('refreshLogs');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            fetchLogs();
        });
    }

    // 初始化页面时获取成员列表
    fetchMembersWithFilter();

    // 初始化最近活动 - 确保只调用一次
    if (typeof fetchRecentActivities === 'function') {
        fetchRecentActivities();

        // 添加刷新按钮事件
        const refreshActivitiesBtn = document.getElementById('refreshActivities');
        if (refreshActivitiesBtn) {
            refreshActivitiesBtn.addEventListener('click', function() {
                fetchRecentActivities();
                showNotification('活动数据已刷新', 'success');
            });
        }

        // 每2分钟自动刷新活动数据
        setInterval(fetchRecentActivities, 120000);
    }
});