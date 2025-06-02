// 处理登录表单提交
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // 这里后续会添加与后端的交互
        console.log('登录信息：', { username, password });
        
        // 模拟登录成功
        alert('登录成功！');
        window.location.href = 'index.html';
    });
}

// 处理注册表单提交
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        // 简单的表单验证
        if (password !== confirmPassword) {
            alert('两次输入的密码不一致！');
            return;
        }

        // 这里后续会添加与后端的交互
        console.log('注册信息：', { username, email, password });
        
        // 模拟注册成功
        alert('注册成功！');
        window.location.href = 'login.html';
    });
}

// 表单验证
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// 添加输入验证样式
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            if (!input.value.trim()) {
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });
    });
}); 