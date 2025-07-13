// static/js/pomodoro.js
document.addEventListener('DOMContentLoaded', function() {
    // 获取 DOM 元素
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resetBtn = document.getElementById('resetBtn');
    const workTimeInput = document.getElementById('workTime');
    const workTimeValue = document.getElementById('workTimeValue');
    const shortBreakInput = document.getElementById('shortBreak');
    const shortBreakValue = document.getElementById('shortBreakValue');
    const longBreakInput = document.getElementById('longBreak');
    const longBreakValue = document.getElementById('longBreakValue');
    const progressElement = document.getElementById('progress');
    const progressTextElement = document.getElementById('progressText');
    const completedSessionsElement = document.getElementById('completedSessions');
    const currentStreakElement = document.getElementById('currentStreak');
    const totalTimeElement = document.getElementById('totalTime');
    const lightModeBtn = document.getElementById('lightMode');
    const darkModeBtn = document.getElementById('darkMode');
    const gradientModeBtn = document.getElementById('gradientMode');
    const fullScreenBtn = document.getElementById('fullScreen');

    // 状态变量
    let timer;
    let secondsLeft;
    let isRunning = false;
    let currentMode = 'work';
    let completedSessions = 0;
    let currentStreak = 0;
    let totalTime = 0;

    // 初始化
    workTimeValue.textContent = workTimeInput.value;
    shortBreakValue.textContent = shortBreakInput.value;
    longBreakValue.textContent = longBreakInput.value;

    // 更新计时器显示
    function updateDisplay() {
        const minutes = Math.floor(secondsLeft / 60);
        const seconds = secondsLeft % 60;
        minutesElement.textContent = minutes.toString().padStart(2, '0');
        secondsElement.textContent = seconds.toString().padStart(2, '0');
    }

    // 更新进度条
    function updateProgress(elapsed, total) {
        const percentage = (elapsed / total) * 100;
        progressElement.style.width = `${percentage}%`;
    }

    // 更新进度文本
    function updateProgressText() {
        if (isRunning) {
            if (currentMode === 'work') {
                progressTextElement.textContent = '工作时间';
            } else if (currentMode === 'shortBreak') {
                progressTextElement.textContent = '短休息时间';
            } else if (currentMode === 'longBreak') {
                progressTextElement.textContent = '长休息时间';
            }
        } else {
            progressTextElement.textContent = '准备开始';
        }
    }

    // 开始计时器
    function startTimer() {
        if (isRunning) return;

        isRunning = true;
        startBtn.disabled = true;
        pauseBtn.disabled = false;

        const totalSeconds = currentMode === 'work'
            ? workTimeInput.value * 60
            : currentMode === 'shortBreak'
                ? shortBreakInput.value * 60
                : longBreakInput.value * 60;

        secondsLeft = totalSeconds;
        updateDisplay();

        timer = setInterval(function() {
            secondsLeft--;
            updateDisplay();
            updateProgress(totalSeconds - secondsLeft, totalSeconds);

            if (secondsLeft <= 0) {
                clearInterval(timer);
                isRunning = false;
                startBtn.disabled = false;
                pauseBtn.disabled = true;

                if (currentMode === 'work') {
                    completedSessions++;
                    currentStreak++;
                    completedSessionsElement.textContent = completedSessions;
                    currentStreakElement.textContent = currentStreak;

                    // 每完成4个工作周期后进入长休息
                    if (completedSessions % 4 === 0) {
                        currentMode = 'longBreak';
                    } else {
                        currentMode = 'shortBreak';
                    }
                } else {
                    currentMode = 'work';
                }

                // 更新进度文本
                updateProgressText();
            }
        }, 1000);
    }

    // 暂停计时器
    function pauseTimer() {
        if (!isRunning) return;

        clearInterval(timer);
        isRunning = false;
        startBtn.disabled = false;
        pauseBtn.disabled = true;
    }

    // 重置计时器
    function resetTimer() {
        clearInterval(timer);
        isRunning = false;
        startBtn.disabled = false;
        pauseBtn.disabled = true;

        // 根据当前模式重置时间
        if (currentMode === 'work') {
            secondsLeft = workTimeInput.value * 60;
        } else if (currentMode === 'shortBreak') {
            secondsLeft = shortBreakInput.value * 60;
        } else {
            secondsLeft = longBreakInput.value * 60;
        }

        updateDisplay();
        progressElement.style.width = '0%';
        updateProgressText();
    }

    // 更新设置值显示
    function updateSettingValue(event) {
        const valueDisplay = event.target.nextElementSibling;
        valueDisplay.textContent = event.target.value;
    }

    // 更新统计数据
    function updateStatistics() {
        totalTimeElement.textContent = Math.floor(totalTime / 60) + ' 分钟';
    }

    // 切换主题模式
    function toggleMode(mode) {
        document.body.className = mode;
        lightModeBtn.classList.remove('active');
        darkModeBtn.classList.remove('active');
        gradientModeBtn.classList.remove('active');

        if (mode === 'light-mode') {
            lightModeBtn.classList.add('active');
        } else if (mode === 'dark-mode') {
            darkModeBtn.classList.add('active');
        } else if (mode === 'gradient-mode') {
            gradientModeBtn.classList.add('active');
        }
    }

    // 切换全屏模式
    function toggleFullScreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            document.body.classList.add('fullscreen');
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
            document.body.classList.remove('fullscreen');
        }
    }

    // 事件监听器
    startBtn.addEventListener('click', startTimer);
    pauseBtn.addEventListener('click', pauseTimer);
    resetBtn.addEventListener('click', resetTimer);

    workTimeInput.addEventListener('input', updateSettingValue);
    shortBreakInput.addEventListener('input', updateSettingValue);
    longBreakInput.addEventListener('input', updateSettingValue);

    lightModeBtn.addEventListener('click', function() {
        toggleMode('light-mode');
    });

    darkModeBtn.addEventListener('click', function() {
        toggleMode('dark-mode');
    });

    gradientModeBtn.addEventListener('click', function() {
        toggleMode('gradient-mode');
    });

    fullScreenBtn.addEventListener('click', toggleFullScreen);

    // 初始化
    updateProgressText();
    toggleMode('light-mode');
});