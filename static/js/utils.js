/**
 * 工具函数模块
 * 封装通用 DOM 操作、事件处理、格式化函数
 */

const Utils = {
    /**
     * DOM 查询简写
     */
    $(selector, context = document) {
        return context.querySelector(selector);
    },
    
    $$(selector, context = document) {
        return context.querySelectorAll(selector);
    },
    
    /**
     * 创建带类名的元素
     */
    createElement(tag, className, html = '') {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (html) el.innerHTML = html;
        return el;
    },
    
    /**
     * 防抖函数
     */
    debounce(fn, delay = CONFIG.ANIMATION.DEBOUNCE_DELAY) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    },
    
    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * 检查文件类型是否允许
     */
    isValidFileType(filename) {
        return CONFIG.FILE.ALLOWED_TYPES.some(type => 
            filename.toLowerCase().endsWith(type)
        );
    },
    
    /**
     * 显示/隐藏元素
     */
    toggleVisibility(element, show) {
        if (show) {
            element.classList.add('is-visible');
            element.style.display = '';
        } else {
            element.classList.remove('is-visible');
            element.style.display = 'none';
        }
    },
    
    /**
     * 设置加载状态
     */
    setLoading(button, isLoading) {
        button.disabled = isLoading;
        const spinner = button.querySelector('.loading');
        if (spinner) {
            spinner.style.display = isLoading ? 'inline-block' : 'none';
        }
    },
    
    /**
     * 安全的 fetch 封装
     */
    async fetchJSON(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Accept': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }
};