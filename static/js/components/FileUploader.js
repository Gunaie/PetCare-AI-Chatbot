/**
 * 文件上传组件
 * 封装所有上传相关的逻辑和 UI
 */
class FileUploader {
    constructor(containerId) {
        this.container = Utils.$(`#${containerId}`);
        this.selectedFiles = [];
        this.init();
    }
    
    /**
     * 初始化组件
     */
    init() {
        this.render();
        this.bindEvents();
    }
    
    /**
     * 渲染组件 HTML
     */
    render() {
        this.container.innerHTML = `
            <h2 class="card-title">📚 上传知识库</h2>
            
            <div class="upload-zone" id="upload-zone">
                <input type="file" id="file-input" accept="${CONFIG.FILE.ALLOWED_TYPES.join(',')}" multiple hidden>
                
                <div class="upload-zone__content">
                    <p class="upload-zone__title">📁 点击选择文件</p>
                    <p class="upload-zone__hint">或拖拽文件到此处</p>
                    <p class="upload-zone__sub-hint">支持同时上传多个 PDF/TXT 文件</p>
                </div>
                
                <div class="file-list" id="file-list"></div>
                
                <button class="btn" id="upload-btn" style="display: none; margin-top: 16px;">
                    开始上传
                    <span class="loading" style="display: none;"></span>
                </button>
                
                <div class="upload-summary" id="upload-summary" style="display: none;"></div>
            </div>
            
            <div class="tips">
                💡 建议上传：宠物疫苗指南、常见疾病手册、训练教程、营养搭配表
            </div>
        `;
        
        // 缓存 DOM 引用
        this.zone = Utils.$('#upload-zone');
        this.input = Utils.$('#file-input');
        this.fileList = Utils.$('#file-list');
        this.uploadBtn = Utils.$('#upload-btn');
        this.summary = Utils.$('#upload-summary');
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 点击上传
        this.zone.addEventListener('click', (e) => {
            if (e.target !== this.uploadBtn && !this.uploadBtn.contains(e.target)) {
                this.input.click();
            }
        });
        
        // 文件选择
        this.input.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
        
        // 拖拽事件
        this.zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.zone.classList.add('is-dragover');
        });
        
        this.zone.addEventListener('dragleave', () => {
            this.zone.classList.remove('is-dragover');
        });
        
        this.zone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.zone.classList.remove('is-dragover');
            this.handleFiles(e.dataTransfer.files);
        });
        
        // 上传按钮
        this.uploadBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.uploadFiles();
        });
    }
    
    /**
     * 处理文件选择
     */
    handleFiles(files) {
        Array.from(files).forEach(file => {
            if (!Utils.isValidFileType(file.name)) return;
            
            // 去重
            const exists = this.selectedFiles.some(f => f.name === file.name);
            if (!exists) {
                this.selectedFiles.push(file);
            }
        });
        
        this.renderFileList();
    }
    
    /**
     * 渲染文件列表
     */
    renderFileList() {
        if (this.selectedFiles.length === 0) {
            this.fileList.innerHTML = '';
            this.uploadBtn.style.display = 'none';
            return;
        }
        
        this.fileList.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="file-item" id="file-${index}">
                <span class="file-item__name">${file.name}</span>
                <span class="file-item__status file-item__status--pending" id="status-${index}">
                    ${CONFIG.TEXT.UPLOAD_PENDING}
                </span>
            </div>
        `).join('');
        
        this.uploadBtn.style.display = 'inline-flex';
    }
    
    /**
     * 执行上传
     */
    async uploadFiles() {
        if (this.selectedFiles.length === 0) return;
        
        Utils.setLoading(this.uploadBtn, true);
        this.summary.style.display = 'none';
        
        // 更新状态为上传中
        this.selectedFiles.forEach((_, index) => {
            const statusEl = Utils.$(`#status-${index}`);
            statusEl.textContent = CONFIG.TEXT.UPLOADING;
            statusEl.className = 'file-item__status file-item__status--pending';
        });
        
        const formData = new FormData();
        this.selectedFiles.forEach(file => formData.append('files', file));
        
        try {
            const data = await Utils.fetchJSON(CONFIG.API.UPLOAD, {
                method: 'POST',
                body: formData
            });
            
            this.handleUploadResponse(data);
            
        } catch (error) {
            alert('上传失败: ' + error.message);
        } finally {
            Utils.setLoading(this.uploadBtn, false);
        }
    }
    
    /**
     * 处理上传响应
     */
    handleUploadResponse(data) {
        data.results.forEach((result, index) => {
            const itemEl = Utils.$(`#file-${index}`);
            const statusEl = Utils.$(`#status-${index}`);
            
            // 更新样式
            itemEl.className = `file-item file-item--${result.status}`;
            statusEl.className = `file-item__status file-item__status--${result.status}`;
            
            // 更新文本
            const statusMap = {
                'success': CONFIG.TEXT.UPLOAD_SUCCESS,
                'skipped': CONFIG.TEXT.UPLOAD_SKIPPED,
                'error': CONFIG.TEXT.UPLOAD_ERROR
            };
            statusEl.textContent = statusMap[result.status] || CONFIG.TEXT.UPLOAD_ERROR;
        });
        
        this.summary.textContent = data.summary;
        this.summary.style.display = 'block';
        this.selectedFiles = [];
    }
}