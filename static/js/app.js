/**
 * 应用入口
 * 初始化所有组件
 */

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始化文件上传组件
    const fileUploader = new FileUploader('upload-card');
    
    // 初始化问答组件
    const qaComponent = new QAComponent('qa-card');
    
    console.log('🐱 PetCare AI 应用已启动');
});