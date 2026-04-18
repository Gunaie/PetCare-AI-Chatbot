/**
 * 全局配置模块
 * 集中管理所有常量、API 端点、错误消息
 */
const CONFIG = {
    // API 端点
    API: {
        UPLOAD: '/upload-multiple',
        QUERY: '/query'
    },
    
    // 文件限制
    FILE: {
        ALLOWED_TYPES: ['.pdf', '.txt'],
        MAX_SIZE_MB: 10,
        MAX_FILES: 10
    },
    
    // UI 文本
    TEXT: {
        UPLOAD_SUCCESS: '✓ 成功',
        UPLOAD_SKIPPED: '⚠ 已存在',
        UPLOAD_ERROR: '✗ 失败',
        UPLOAD_PENDING: '等待上传',
        UPLOADING: '上传中...',
        PLACEHOLDER_QUESTION: '例如：猫咪呕吐怎么办？',
        NO_SOURCES: '无'
    },
    
    // 动画时间
    ANIMATION: {
        DEBOUNCE_DELAY: 300,
        LOADING_DELAY: 150
    }
};

// 冻结配置防止运行时修改
Object.freeze(CONFIG);