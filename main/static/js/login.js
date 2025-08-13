document.addEventListener('DOMContentLoaded', () => {
    // 密码可见性切换
    const togglePassword = document.querySelector('.show-password');
    if (togglePassword) {
        const passwordInput = document.getElementById('password');
        togglePassword.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                togglePassword.textContent = 'visibility';
            } else {
                passwordInput.type = 'password';
                togglePassword.textContent = 'visibility_off';
            }
        });
    }

    // 显示当前登录用户信息
    async function displayCurrentUser() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                // 如果没有令牌，检查是否在登录页面，是的话不执行任何操作
                if (window.location.pathname.includes('login.html')) {
                    return;
                } else {
                    // 如果在其他页面，则重定向到登录页面
                    window.location.href = 'login.html';
                }
            }

            const response = await fetch('http://localhost:5000/api/current-user', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                // 更新登录页面显示
                document.getElementById('username').value = data.display_name;

                // 显示登录信息
                const loginInfo = document.getElementById('loginInfo');
                const userInfo = document.getElementById('userInfo');
                const loginTime = document.getElementById('loginTime');

                if (userInfo) {
                    userInfo.textContent = `用户名: ${data.display_name}`;
                }

                if (loginTime) {
                    loginTime.textContent = `登录时间: ${new Date().toLocaleString()}`;
                }

                if (loginInfo) {
                    loginInfo.style.display = 'block';
                }

                // 隐藏登录表单
                const loginForm = document.getElementById('loginForm');
                if (loginForm) {
                    loginForm.style.display = 'none';
                }

                // 显示退出按钮
                const logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {
                    logoutBtn.style.display = 'block';
                }
            } else {
                console.error('获取当前用户失败:', data.error);
                // 如果获取当前用户失败，重定向到登录页面
                window.location.href = 'login.html';
            }
        } catch (error) {
            console.error('获取当前用户失败:', error);
            // 如果发生错误，重定向到登录页面
            window.location.href = 'login.html';
        }
    }

    // 初始化显示当前用户
    displayCurrentUser();

    // 登录表单提交
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // 阻止表单默认提交行为

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('http://localhost:5000/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ login_id: username, password }), // 使用 login_id
                });

                const result = await response.json();

                if (response.ok) {
                    // 存储令牌和用户信息
                    localStorage.setItem('token', result.token);
                    localStorage.setItem('user', JSON.stringify({
                        username: result.username,
                        level: result.level,
                        display_name: result.display_name,
                        last_login: result.last_login,
                        is_online: true  // 假设登录时为在线状态
                    }));

                    // 登录成功后重定向
                    window.location.href = 'main.html';
                } else {
                    // 显示错误消息
                    const errorBox = document.createElement('div');
                    errorBox.className = 'error-message';
                    errorBox.textContent = result.error || '登录失败';
                    loginForm.parentNode.insertBefore(errorBox, loginForm);

                    // 3秒后淡出错误消息
                    setTimeout(() => {
                        errorBox.classList.add('error-fade-out');
                        setTimeout(() => {
                            errorBox.remove();
                        }, 300);
                    }, 3000);
                }
            } catch (error) {
                console.error('登录请求失败:', error);
                alert('登录请求失败，请检查网络连接');
            }
        });
    }

    // 退出登录按钮点击事件
    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
        try {
            const token = localStorage.getItem('token');
            if (token) {
                await fetch('http://localhost:5000/api/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            }
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
        } catch (error) {
            console.error('退出登录失败:', error);
            alert('退出登录失败，请检查网络连接');
        }
    });
});