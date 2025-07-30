// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    // 获取当前用户信息
    fetchUserProfile();

    // 获取最近活动
    fetchRecentActivities();

    // 初始化学习统计图表
    initLearningChart();
});

// 获取当前用户信息
function fetchUserProfile() {
    const token = localStorage.getItem('token');

    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    fetch('http://localhost:5000/api/user-profile', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('获取用户信息失败');
        }
        return response.json();
    })
    .then(data => {
        // 更新用户信息
        document.getElementById('profile-name').textContent = data.display_name;
        document.getElementById('profile-role').textContent = `等级 ${data.level}`;
        document.getElementById('profile-bio').textContent = data.bio || '暂无简介';
        document.getElementById('username').textContent = data.username;
        document.getElementById('real-name').textContent = data.real_name || '暂无信息';
        document.getElementById('gender').textContent = data.gender || '暂无信息';
        document.getElementById('grade').textContent = data.grade || '暂无信息';
        document.getElementById('class-info').textContent = data.class_info || '暂无信息';
        document.getElementById('email').textContent = data.email || '暂无信息';
        document.getElementById('registration-date').textContent = data.registration_date || '暂无信息';
        document.getElementById('learning-hours').textContent = data.learning_hours || 0;
        document.getElementById('completed-projects').textContent = data.completed_projects || 0;
        document.getElementById('awards-won').textContent = data.awards_won || 0;

        // 根据等级设置背景颜色
        const levelClass = `level-${data.level}`;
        document.getElementById('profile-header').classList.add(levelClass);
    })
    .catch(error => {
        console.error('获取用户信息错误:', error);
        alert('无法获取用户信息，请重新登录');
        window.location.href = 'login.html';
    });
}

// 获取最近活动
function fetchRecentActivities() {
    const token = localStorage.getItem('token');

    if (!token) {
        return;
    }

    fetch('http://localhost:5000/api/recent-activities', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('获取活动记录失败');
        }
        return response.json();
    })
    .then(data => {
        const activityList = document.getElementById('activity-list');
        activityList.innerHTML = '';

        if (data.length === 0) {
            activityList.innerHTML = '<li class="activity-item"><div class="activity-content"><div class="activity-title">暂无活动记录</div></div></li>';
            return;
        }

        data.forEach(activity => {
            const li = document.createElement('li');
            li.className = 'activity-item';
            li.innerHTML = `
                <div class="activity-icon">
                    <i class="fas ${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-meta">${activity.time} · ${activity.category}</div>
                </div>
            `;
            activityList.appendChild(li);
        });
    })
    .catch(error => {
        console.error('获取活动记录错误:', error);
    });
}

// 初始化学习统计图表
function initLearningChart() {
    const ctx = document.getElementById('learningChart').getContext('2d');
    fetch('http://localhost:5000/api/learning-stats', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: '学习时长 (小时)',
                    data: data.data,
                    backgroundColor: data.backgroundColor,
                    borderColor: data.backgroundColor.map(color => color.replace('0.7)', '1)')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('获取学习统计错误:', error);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['9月', '10月', '11月', '12月', '1月', '2月', '3月'],
                datasets: [{
                    label: '学习时长 (小时)',
                    data: [12, 18, 15, 20, 25, 22, 18],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(231, 76, 60, 0.7)',
                        'rgba(241, 196, 15, 0.7)',
                        'rgba(155, 89, 182, 0.7)',
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)'
                    ],
                    borderColor: [
                        'rgba(52, 152, 219, 1)',
                        'rgba(46, 204, 113, 1)',
                        'rgba(231, 76, 60, 1)',
                        'rgba(241, 196, 15, 1)',
                        'rgba(155, 89, 182, 1)',
                        'rgba(52, 152, 219, 1)',
                        'rgba(46, 204, 113, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    });
}