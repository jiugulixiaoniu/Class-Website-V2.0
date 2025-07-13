// static/js/toolbox.js
document.addEventListener('DOMContentLoaded', function() {
    // 初始化用户认证状态
    initAuthStatus();
});

// 初始化用户认证状态
function initAuthStatus() {
    // 检查登录状态并更新UI
    async function checkAuth() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                // 未登录，显示登录和注册按钮
                document.getElementById('loginBtn').style.display = 'inline-block';
                document.getElementById('registerBtn').style.display = 'inline-block';
                document.getElementById('logoutBtn').style.display = 'none';
                document.getElementById('usernameDisplay').textContent = '';
                document.getElementById('welcomeMessage').textContent = '';
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
                document.getElementById('loginBtn').style.display = 'none';
                document.getElementById('registerBtn').style.display = 'none';
                document.getElementById('logoutBtn').style.display = 'inline-block';
            } else {
                // 令牌无效，显示登录和注册按钮
                document.getElementById('loginBtn').style.display = 'inline-block';
                document.getElementById('registerBtn').style.display = 'inline-block';
                document.getElementById('logoutBtn').style.display = 'none';
                document.getElementById('usernameDisplay').textContent = '';
                document.getElementById('welcomeMessage').textContent = '';
            }
        } catch (error) {
            console.error('认证检查失败:', error);
            // 显示登录和注册按钮
            document.getElementById('loginBtn').style.display = 'inline-block';
            document.getElementById('registerBtn').style.display = 'inline-block';
            document.getElementById('logoutBtn').style.display = 'none';
            document.getElementById('usernameDisplay').textContent = '';
            document.getElementById('welcomeMessage').textContent = '';
        }
    }

    // 退出登录
    document.getElementById('logoutBtn')?.addEventListener('click', async function() {
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
            window.location.href = '/login.html';
        } catch (error) {
            console.error('退出登录失败:', error);
            alert('退出登录失败，请检查网络连接');
        }
    });

    // 初始检查认证状态
    checkAuth();
}