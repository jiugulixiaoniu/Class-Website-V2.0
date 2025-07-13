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
    const searchInput = document.getElementById('memberSearch');
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

// 封装 fetchMembers 函数，添加筛选和排序功能
async function fetchMembersWithFilter() {
    try {
        showLoading(); // 显示加载提示框

        // 获取筛选条件
        const level = document.getElementById('levelFilter') ? document.getElementById('levelFilter').value : '';
        const status = document.getElementById('statusFilter') ? document.getElementById('statusFilter').value : '';
        const searchQuery = document.getElementById('memberSearch') ? document.getElementById('memberSearch').value : '';
        const lastLoginStart = document.getElementById('lastLoginStart') ? document.getElementById('lastLoginStart').value : '';
        const lastLoginEnd = document.getElementById('lastLoginEnd') ? document.getElementById('lastLoginEnd').value : '';
        const createdStart = document.getElementById('createdStart') ? document.getElementById('createdStart').value : '';
        const createdEnd = document.getElementById('createdEnd') ? document.getElementById('createdEnd').value : '';
        const pageSize = document.getElementById('pageSizeSelect') ? document.getElementById('pageSizeSelect').value : 30;
        const currentPage = document.querySelector('.pagination .page-btn.active') ? document.querySelector('.pagination .page-btn.active').textContent : 1;

        // 构建查询参数
        const queryParams = new URLSearchParams({
            level: level,
            status: status,
            search: searchQuery,
            last_login_start: lastLoginStart,
            last_login_end: lastLoginEnd,
            created_start: createdStart,
            created_end: createdEnd,
            page_size: pageSize,
            page: currentPage
        });

        const response = await fetch(`http://localhost:5000/api/members?${queryParams}`);
        if (!response.ok) {
            throw new Error('请求失败');
        }
        const data = await response.json();
        hideLoading(); // 隐藏加载提示框

        // 更新成员列表
        updateMembersTableWithSearch(data.users || data); // 兼容不同返回格式
    } catch (error) {
        console.error('获取成员数据失败:', error);
        showNotification('无法获取成员数据，请检查网络连接', 'error');
        hideLoading(); // 确保隐藏加载提示框
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initNotificationStyles();
    initLoadingStyles();
    initSortingListeners();
    initFilterListeners();
    initPaginationListeners();

    // 初始化页面时获取成员列表
    fetchMembersWithFilter();
});