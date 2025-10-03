// 全局应用脚本

// 显示Toast通知
function showToast(message, type = 'info') {
    const toastBody = document.getElementById('toastBody');
    const toast = document.getElementById('toast');
    
    if (!toastBody || !toast) return;
    
    toastBody.textContent = message;
    
    // 移除之前的类
    toast.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'text-white');
    
    // 根据类型添加相应的类
    switch (type) {
        case 'success':
            toast.classList.add('bg-success', 'text-white');
            break;
        case 'error':
        case 'danger':
            toast.classList.add('bg-danger', 'text-white');
            break;
        case 'warning':
            toast.classList.add('bg-warning', 'text-white');
            break;
        case 'info':
        default:
            toast.classList.add('bg-info', 'text-white');
            break;
    }
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
}

// 退出登录
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            showToast('退出成功', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        } else {
            showToast('退出失败', 'error');
        }
    } catch (error) {
        console.error('退出失败:', error);
        showToast('退出失败', 'error');
    }
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return '今天 ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
    } else if (diffDays === 2) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
    } else if (diffDays <= 7) {
        return diffDays + '天前';
    } else {
        return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
    }
}

// 格式化相对时间
function formatRelativeTime(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now - date;
    const diffMinutes = Math.floor(diffTime / (1000 * 60));
    const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffMinutes < 1) {
        return '刚刚';
    } else if (diffMinutes < 60) {
        return diffMinutes + '分钟前';
    } else if (diffHours < 24) {
        return diffHours + '小时前';
    } else if (diffDays < 30) {
        return diffDays + '天前';
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 验证表单
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// 清除表单验证状态
function clearFormValidation(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('.is-invalid');
    inputs.forEach(input => {
        input.classList.remove('is-invalid');
    });
}

// 处理网络错误
function handleNetworkError(error) {
    console.error('网络错误:', error);
    showToast('网络连接错误，请检查网络后重试', 'error');
}

// 处理API响应
async function handleApiResponse(response) {
    if (!response.ok) {
        if (response.status === 401) {
            showToast('登录已过期，请重新登录', 'warning');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            throw new Error('Unauthorized');
        } else if (response.status === 403) {
            showToast('权限不足', 'error');
            throw new Error('Forbidden');
        } else if (response.status === 404) {
            showToast('请求的资源不存在', 'error');
            throw new Error('Not Found');
        } else if (response.status >= 500) {
            showToast('服务器内部错误，请稍后重试', 'error');
            throw new Error('Server Error');
        }
    }
    return response;
}

// API请求封装
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        await handleApiResponse(response);
        return response;
    } catch (error) {
        handleNetworkError(error);
        throw error;
    }
}

// 确认对话框
function confirmDialog(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 加载状态管理
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
            </div>
        `;
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// 本地存储工具
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('存储数据失败:', error);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('读取数据失败:', error);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('删除数据失败:', error);
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('清空数据失败:', error);
        }
    }
};

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // 设置当前页面的导航高亮
    setActiveNavigation();
    
    // 添加表单验证
    addFormValidation();
});

// 设置当前页面的导航高亮
function setActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// 添加表单验证
function addFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.value.trim()) {
                    this.classList.remove('is-invalid');
                }
            });
        });
    });
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('已复制到剪贴板', 'success');
    } catch (error) {
        console.error('复制失败:', error);
        showToast('复制失败', 'error');
    }
}

// 导出数据为CSV
function exportToCSV(data, filename) {
    if (!data || !data.length) {
        showToast('没有数据可导出', 'warning');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('导出成功', 'success');
    } else {
        showToast('浏览器不支持导出功能', 'error');
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 全局错误处理
window.addEventListener('error', function(event) {
    console.error('全局错误:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('未处理的Promise拒绝:', event.reason);
});

// 导出工具函数供其他脚本使用
window.utils = {
    showToast,
    formatDate,
    formatRelativeTime,
    validateForm,
    clearFormValidation,
    handleNetworkError,
    handleApiResponse,
    apiRequest,
    confirmDialog,
    showLoading,
    hideLoading,
    storage,
    copyToClipboard,
    exportToCSV,
    debounce,
    throttle
};