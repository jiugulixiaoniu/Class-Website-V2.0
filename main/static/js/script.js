// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // 移动端菜单切换
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            this.querySelector('i').classList.toggle('fa-bars');
            this.querySelector('i').classList.toggle('fa-times');
        });
    }

    // 卡片悬停效果增强
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // 相册悬停效果
    const galleryItems = document.querySelectorAll('.gallery-item');
    galleryItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.querySelector('.gallery-overlay').style.transform = 'translateY(0)';
            this.querySelector('.gallery-overlay').style.opacity = '1';
        });

        item.addEventListener('mouseleave', function() {
            this.querySelector('.gallery-overlay').style.transform = 'translateY(20px)';
            this.querySelector('.gallery-overlay').style.opacity = '0';
        });
    });

    // 滚动动画
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // 观察需要动画的元素
    document.querySelectorAll('.card, .timeline-item, .gallery-item').forEach(el => {
        observer.observe(el);
    });
});
// 时钟功能
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
// 初始化时钟并每秒更新
updateClock();
setInterval(updateClock, 1000);