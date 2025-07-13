document.addEventListener('DOMContentLoaded', () => {
    // 切换密码可见性
    const togglePasswords = document.querySelectorAll('.show-password');
    togglePasswords.forEach(toggle => {
        const passwordInput = toggle.previousElementSibling;
        toggle.addEventListener('click', () => {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggle.textContent = 'visibility';
            } else {
                passwordInput.type = 'password';
                toggle.textContent = 'visibility_off';
            }
        });
    });

    // 注册表单提交
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // 阻止表单默认提交行为

            const username = document.getElementById('username').value;
            const display_name = document.getElementById('display_name').value;
            const password = document.getElementById('password').value;
            const confirm_password = document.getElementById('confirm_password').value;
            const phone = document.getElementById('phone').value;
            const email = document.getElementById('email').value;

            // 验证密码是否匹配
            if (password !== confirm_password) {
                showNotification('两次输入的密码不一致', 'error');
                return;
            }

            // 检查是否至少填写了电话号码或电子邮箱
            if (!phone && !email) {
                showNotification('请至少填写电话号码或电子邮箱', 'error');
                return;
            }

            // 如果未填写电话号码，则设置为 "unregistered"
            const phoneToSend = phone || "unregistered";

            // 如果未填写电子邮箱，则设置为 "unregistered"
            const emailToSend = email || "unregistered";

            try {
                const response = await fetch('http://localhost:5000/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, display_name, password, phone: phoneToSend, email: emailToSend }),
                });

                const result = await response.json();

                if (response.ok) {
                    // 注册成功
                    showNotification('注册成功！请前往登录页面', 'success');
                    window.location.href = 'login.html';
                } else {
                    // 显示错误消息
                    showNotification(result.error || '注册失败', 'error');
                }
            } catch (error) {
                console.error('注册请求失败:', error);
                showNotification('注册请求失败，请检查网络连接', 'error');
            }
        });
    }

    // 显示通知
    function showNotification(message, type = 'success') {
        const notificationElement = document.createElement('div');
        notificationElement.className = `notification ${type}`;
        notificationElement.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${type === 'success' ? 'fa-check' : 'fa-times'}"></i>
            </div>
            <div class="notification-content">
                ${message}
            </div>
            <div class="notification-progress-bar"></div>
        `;
        document.body.appendChild(notificationElement);

        // 添加动画
        setTimeout(() => {
            notificationElement.classList.add('show');
        }, 10);

        // 自动关闭通知
        setTimeout(() => {
            notificationElement.classList.remove('show');
            setTimeout(() => {
                notificationElement.remove();
            }, 300);
        }, 3000);

        // 添加通知样式
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 350px;
                margin-bottom: 15px;
                padding: 20px;
                border-radius: 8px;
                color: white;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
                transform: translateX(150%);
                transition: transform 0.3s ease-out;
                z-index: 1000;
            }

            .notification.success {
                background: linear-gradient(135deg, #4CAF50, #2E7D32);
            }

            .notification.error {
                background: linear-gradient(135deg, #F44336, #D32F2F);
            }

            .notification .notification-icon {
                font-size: 24px;
                margin-right: 15px;
            }

            .notification.show {
                transform: translateX(0);
            }

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
        `;
        document.head.appendChild(style);
    }
});