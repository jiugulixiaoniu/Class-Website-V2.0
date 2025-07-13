// 检查登录状态并更新UI
async function checkAuth() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            // 未登录，显示登录和注册按钮
            if (document.getElementById('loginBtn')) {
                document.getElementById('loginBtn').style.display = 'inline-block';
            }
            if (document.getElementById('registerBtn')) {
                document.getElementById('registerBtn').style.display = 'inline-block';
            }
            if (document.getElementById('logoutBtn')) {
                document.getElementById('logoutBtn').style.display = 'none';
            }
            if (document.getElementById('usernameDisplay')) {
                document.getElementById('usernameDisplay').textContent = '';
            }
            if (document.getElementById('welcomeMessage')) {
                document.getElementById('welcomeMessage').textContent = '';
            }

            // 处理 admin.html 页面
            if (window.location.pathname.includes('admin.html')) {
                window.location.href = 'login.html';
            }

            return;
        }

        const response = await fetch('http://localhost:5000/api/validate', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            // 已登录，更新页面显示
            const usernameElement = document.getElementById('usernameDisplay');
            const userDisplay = data.payload.username;
            if (usernameElement) {
                usernameElement.textContent = userDisplay;
            }

            const welcomeMessage = document.getElementById('welcomeMessage');
            if (welcomeMessage) {
                welcomeMessage.textContent = '，欢迎回来';
            }

            // 隐藏登录和注册按钮，显示退出按钮
            if (document.getElementById('loginBtn')) {
                document.getElementById('loginBtn').style.display = 'none';
            }
            if (document.getElementById('registerBtn')) {
                document.getElementById('registerBtn').style.display = 'none';
            }
            if (document.getElementById('logoutBtn')) {
                document.getElementById('logoutBtn').style.display = 'inline-block';
            }
        } else {
            // 令牌无效，显示登录和注册按钮
            if (document.getElementById('loginBtn')) {
                document.getElementById('loginBtn').style.display = 'inline-block';
            }
            if (document.getElementById('registerBtn')) {
                document.getElementById('registerBtn').style.display = 'inline-block';
            }
            if (document.getElementById('logoutBtn')) {
                document.getElementById('logoutBtn').style.display = 'none';
            }
            if (document.getElementById('usernameDisplay')) {
                document.getElementById('usernameDisplay').textContent = '';
            }
            if (document.getElementById('welcomeMessage')) {
                document.getElementById('welcomeMessage').textContent = '';
            }

            // 处理 admin.html 页面
            if (window.location.pathname.includes('admin.html')) {
                window.location.href = 'login.html';
            }
        }
    } catch (error) {
        console.error('认证检查失败:', error);
        // 显示登录和注册按钮
        if (document.getElementById('loginBtn')) {
            document.getElementById('loginBtn').style.display = 'inline-block';
        }
        if (document.getElementById('registerBtn')) {
            document.getElementById('registerBtn').style.display = 'inline-block';
        }
        if (document.getElementById('logoutBtn')) {
            document.getElementById('logoutBtn').style.display = 'none';
        }
        if (document.getElementById('usernameDisplay')) {
            document.getElementById('usernameDisplay').textContent = '';
        }
        if (document.getElementById('welcomeMessage')) {
            document.getElementById('welcomeMessage').textContent = '';
        }

        // 处理 admin.html 页面
        if (window.location.pathname.includes('admin.html')) {
            window.location.href = 'login.html';
        }
    }
}

// 显示当前登录用户
async function displayCurrentUser() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            return;
        }

        const response = await fetch('http://localhost:5000/api/current-user', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        });

        const data = await response.json();

        if (response.ok) {
            // 更新页面显示
            if (document.getElementById('usernameDisplay')) {
                document.getElementById('usernameDisplay').textContent = data.display_name;
            }
            if (document.getElementById('current-user')) {
                document.getElementById('current-user').textContent = data.display_name;
            }
        } else {
            console.error('获取当前用户失败:', data.error);
        }
    } catch (error) {
        console.error('获取当前用户失败:', error);
    }
}

// 初始化时检查认证状态
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    displayCurrentUser();
});

// 退出登录
if (document.getElementById('logoutBtn')) {
    document.getElementById('logoutBtn').addEventListener('click', async function() {
        try {
            const token = localStorage.getItem('token');
            if (token) {
                await fetch('http://localhost:5000/api/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + token
                    }
                });
            }
            localStorage.removeItem('token');
            window.location.href = '/login';
        } catch (error) {
            console.error('退出登录失败:', error);
            alert('退出登录失败，请检查网络连接');
        }
    });
}