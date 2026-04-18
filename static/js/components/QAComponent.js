/**
 * 问答组件
 * 封装提问和答案展示逻辑
 */
class QAComponent {
    constructor(containerId) {
        this.container = Utils.$(`#${containerId}`);
        this.init();
    }
    
    init() {
        this.render();
        this.bindEvents();
    }
    
    render() {
        this.container.innerHTML = `
            <h2 class="card-title">💬 宠物知识问答</h2>
            
            <input type="text" 
                   class="input" 
                   id="question-input"
                   placeholder="${CONFIG.TEXT.PLACEHOLDER_QUESTION}">
            
            <button class="btn" id="ask-btn" style="margin-top: 16px;">
                提问
                <span class="loading" style="display: none;"></span>
            </button>
            
            <div class="result" id="qa-result">
                <div class="result__content" id="answer-content"></div>
                <div class="result__sources" id="sources-content"></div>
            </div>
        `;
        
        this.input = Utils.$('#question-input');
        this.askBtn = Utils.$('#ask-btn');
        this.result = Utils.$('#qa-result');
        this.answerContent = Utils.$('#answer-content');
        this.sourcesContent = Utils.$('#sources-content');
    }
    
    bindEvents() {
        this.askBtn.addEventListener('click', () => this.ask());
        
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.ask();
        });
    }
    
    async ask() {
        const question = this.input.value.trim();
        if (!question) {
            alert('请输入问题');
            return;
        }
        
        Utils.setLoading(this.askBtn, true);
        Utils.toggleVisibility(this.result, false);
        
        const formData = new FormData();
        formData.append('question', question);
        
        try {
            const data = await Utils.fetchJSON(CONFIG.API.QUERY, {
                method: 'POST',
                body: formData
            });
            
            this.displayResult(data);
            
        } catch (error) {
            alert('查询失败: ' + error.message);
        } finally {
            Utils.setLoading(this.askBtn, false);
        }
    }
    
    displayResult(data) {
        // 渲染答案（支持换行）
        this.answerContent.innerHTML = data.answer
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // 支持 **粗体**
        
        // 渲染来源
        const sourcesHtml = data.sources?.length > 0
            ? data.sources.join('<br><br>')
            : CONFIG.TEXT.NO_SOURCES;
        
        this.sourcesContent.innerHTML = `<strong>📖 参考来源：</strong><br>${sourcesHtml}`;
        
        Utils.toggleVisibility(this.result, true);
    }
}