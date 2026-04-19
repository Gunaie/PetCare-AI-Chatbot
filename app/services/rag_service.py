# app/services/rag_service.py
"""RAG核心服务：协调检索和生成"""

from app.infrastructure.database.chroma_repository import ChromaRepository
from app.infrastructure.ai.embeddings import LocalEmbeddingService
from app.infrastructure.ai.llm import DeepSeekService
from typing import List, Dict, Any, Tuple
import os
import re
from app.config import settings
from app.domain.repositories import VectorRepository
from app.infrastructure.database.chroma_repository import ChromaRepository
from app.infrastructure.ai.embeddings import LocalEmbeddingService
from app.infrastructure.ai.llm import DeepSeekService
from app.services.interfaces import RAGServiceInterface
from app.services.interfaces import RAGServiceInterface
from app.services.document_service import DocumentService
from app.config import settings


class RAGService(RAGServiceInterface):
    """RAG服务实现"""
    
    def __init__(
        self,
        vector_repo: VectorRepository = None,
        document_service: DocumentService = None,
        llm_service: DeepSeekService = None
    ):
        self.vector_repo = vector_repo or ChromaRepository()
        self.doc_service = document_service or DocumentService()
        self.llm = llm_service or DeepSeekService()
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """添加文档到知识库"""
        filename = os.path.basename(file_path)
        
        # 检查重复
        if self.vector_repo.exists(filename):
            return {
                "status": "skipped",
                "message": f"文档 [{filename}] 已存在",
                "filename": filename
            }
        
        try:
            # 处理文档
            doc, chunks = self.doc_service.process_file(file_path)
            
            if not chunks:
                return {
                    "status": "error",
                    "message": "未能生成有效文本块",
                    "filename": filename
                }
            
            # 存储到向量库
            self.vector_repo.add_chunks(chunks)
            
            return {
                "status": "success",
                "message": f"成功添加 {len(chunks)} 个片段",
                "filename": filename,
                "chunk_count": len(chunks),
                "char_count": len(doc.content)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "filename": filename
            }
    
    def _is_directly_relevant(self, text: str, answer: str) -> Tuple[bool, str, str]:
        """
        严格判断文本是否与答案直接相关
        返回：(是否相关, 匹配类型, 匹配内容)
        """
        if not text or not answer:
            return False, "无内容", ""
        
        text_lower = text.lower()
        answer_lower = answer.lower()
        
        # 1. 完全包含答案核心句子（最强匹配）
        # 提取答案中的关键句（通常包含数字）
        answer_sentences = re.split(r'[。！？.!?]', answer_lower)
        for sent in answer_sentences:
            sent = sent.strip()
            if len(sent) > 10 and sent in text_lower:
                return True, "完全包含", sent[:30]
        
        # 2. 数字精确匹配（强信号）
        answer_numbers = set(re.findall(r'\d+', answer))
        text_numbers = set(re.findall(r'\d+', text))
        
        # 必须包含答案中的关键数字（如"20"）
        number_overlap = answer_numbers & text_numbers
        if len(number_overlap) >= 1:
            # 检查这些数字是否在相似的上下文中（如"20岁"、"20年"）
            for num in number_overlap:
                # 检查数字周围是否有年龄/寿命相关词
                pattern = rf'{num}\s*[岁年]'
                if re.search(pattern, text) or re.search(pattern, answer):
                    return True, f"数字匹配:{num}", num
        
        # 3. 关键短语多重匹配（至少2个独立短语）
        # 提取答案中的实体短语（过滤虚词）
        stop_words = {'这是', '一个', '可以', '能够', '它们', '有些', '如果', 
                     '得到', '良好', '照顾', '甚至', '更久', '但是', '因此',
                     '以上', '以下', '因此', '所以', '因为', '而且'}
        
        # 提取2-4字的关键短语
        phrases = re.findall(r'[\u4e00-\u9fff]{2,4}', answer)
        key_phrases = [p for p in phrases if p not in stop_words and len(p) >= 2]
        
        # 去重并限制数量
        key_phrases = list(set(key_phrases))[:5]
        
        match_count = 0
        matched_phrases = []
        for phrase in key_phrases:
            if phrase in text:
                match_count += 1
                matched_phrases.append(phrase)
        
        # 必须匹配至少2个独立短语，或1个非常具体的短语（如"20多岁"）
        if match_count >= 2:
            return True, f"短语匹配:{matched_phrases}", ",".join(matched_phrases[:2])
        
        # 特殊：包含"20多岁"这种非常具体的表达
        specific_patterns = ['20多岁', '20岁', '20年', '二十多岁', '二十岁']
        for pattern in specific_patterns:
            if pattern in text or pattern in answer and pattern in text:
                return True, f"特定表达:{pattern}", pattern
        
        # 4. 主题一致性检查（排除明显无关的主题）
        # 如果文本包含明显偏离的主题，直接拒绝
        irrelevant_markers = {
            '绝育': '繁殖主题',
            '手术': '医疗操作主题', 
            '品种': '分类主题',
            '毛色': '外观主题',
            '培育': '育种主题',
            '狗': '其他动物主题'
        }
        
        for marker, topic in irrelevant_markers.items():
            if marker in text and marker not in answer:
                # 文本包含答案中没有的偏离主题
                return False, f"主题偏离:{topic}", marker
        
        # 5. 默认：不相关
        return False, "无显著匹配", ""
    
    def _extract_relevant_snippet(self, text: str, answer: str, max_len: int = 85) -> str:
        """
        从文本中提取与答案最相关的片段
        优先选择包含答案关键信息的句子
        """
        if not text:
            return ""
        
        # 清洗
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 提取答案关键信息
        answer_numbers = set(re.findall(r'\d+', answer))
        answer_phrases = set(re.findall(r'[\u4e00-\u9fff]{3,5}', answer))  # 3-5字更精确
        
        # 分割句子
        raw_sentences = re.split(r'([。！？.!?])', text)
        sentences = []
        for i in range(0, len(raw_sentences)-1, 2):
            if i+1 < len(raw_sentences):
                sent = raw_sentences[i] + raw_sentences[i+1]
            else:
                sent = raw_sentences[i]
            sent = sent.strip()
            if len(sent) > 15:
                sentences.append(sent)
        
        if not sentences:
            return text[:max_len] + "..." if len(text) > max_len else text
        
        # 评分选择最佳句子
        best_score = -100
        best_sent = sentences[0]
        
        for sent in sentences:
            score = 0
            sent_lower = sent.lower()
            
            # 包含数字匹配（最高权重）
            sent_numbers = set(re.findall(r'\d+', sent))
            num_matches = sent_numbers & answer_numbers
            score += len(num_matches) * 10  # 数字匹配权重极高
            
            # 包含答案中的关键短语
            phrase_matches = 0
            for phrase in answer_phrases:
                if phrase in sent:
                    phrase_matches += 1
                    score += 3
            
            # 包含答案中的完整子串（强信号）
            # 提取答案中的关键子串（8-15字）
            for length in [15, 12, 10, 8]:
                for i in range(len(answer) - length + 1):
                    substring = answer[i:i+length]
                    if len(substring) >= 8 and substring in sent:
                        score += 5
                        break
            
            # 长度适中
            if 30 <= len(sent) <= max_len:
                score += 1
            
            # 惩罚：包含明显无关词汇
            irrelevant_words = ['绝育', '手术', '品种', '毛色', '培育', '狗 ', '犬类']
            for word in irrelevant_words:
                if word in sent and word not in answer:
                    score -= 8
            
            if score > best_score:
                best_score = score
                best_sent = sent
        
        # 截断
        if len(best_sent) > max_len:
            for punct in ['。', '！', '？', '.']:
                pos = best_sent[:max_len].rfind(punct)
                if pos > max_len * 0.5:
                    return best_sent[:pos+1]
            return best_sent[:max_len-3] + "..."
        
        return best_sent
    
    def query(self, question: str) -> Dict[str, Any]:
        """RAG查询"""
        # 1. 嵌入查询
        query_embedding = self.doc_service.embedder.embed_query(question)
        
        # 2. 检索相关块
        chunks = self.vector_repo.search(query_embedding, top_k=5)
        
        disclaimer = "⚠️ 免责声明：以上信息仅供参考，宠物健康问题请务必咨询专业兽医。"
        
        if not chunks:
            return {
                "answer": f"知识库中没有相关内容\n\n{disclaimer}",
                "sources": []
            }
        
        # 3. 去重
        unique_chunks = []
        seen = set()
        for chunk in chunks:
            fingerprint = chunk.content[:100]
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique_chunks.append(chunk)
        
        # 4. 构建上下文
        context = "\n\n".join([c.content for c in unique_chunks[:3]])
        
        # 5. 生成提示词
        prompt = f"""基于以下知识库内容回答问题：

【知识库内容】
{context}

【问题】
{question}

回答要求：
1. 简洁直接，给出具体答案，不要寒暄
2. 只回答用户问的问题，不要扩展无关内容
3. 基于知识库内容回答，不要编造
4. 如知识库无相关信息，回答"根据现有资料无法确定"

【强制要求 - 必须遵守】
你的回答必须严格按以下格式输出：
1. 首先给出问题的直接回答
2. 然后换行，单独输出以下免责声明（一字不差，不得省略）：

{disclaimer}

请严格按格式回答："""
        
        # 6. 调用LLM
        answer = self.llm.generate(prompt)
        
        # 7. 安全检查：确保有免责声明
        if disclaimer not in answer:
            answer = answer.strip() + "\n\n" + disclaimer
        
        # 8. 严格来源筛选：只保留直接相关的
        uncertain_indicators = [
            "根据现有资料无法确定",
            "无法确定",
            "知识库中没有相关内容",
            "没有相关信息"
        ]
        
        is_uncertain = any(indicator in answer for indicator in uncertain_indicators)
        
        if is_uncertain:
            sources = []
        else:
            # 严格过滤：只保留直接相关的来源
            sources = []
            idx = 1
            
            for chunk in unique_chunks:
                filename = chunk.metadata.get('filename', '未知文件')
                
                # 严格相关性判断
                is_relevant, match_type, match_content = self._is_directly_relevant(chunk.content, answer)
                
                if not is_relevant:
                    # 完全不相关，跳过
                    continue
                
                # 提取相关片段
                snippet = self._extract_relevant_snippet(chunk.content, answer, max_len=85)
                
                # 最终验证：片段必须包含关键信息
                if snippet and len(snippet) > 15:
                    # 再次验证片段包含答案中的数字或关键短语
                    has_number = bool(set(re.findall(r'\d+', snippet)) & set(re.findall(r'\d+', answer)))
                    has_phrase = any(p in snippet for p in re.findall(r'[\u4e00-\u9fff]{3,5}', answer)[:3])
                    
                    if has_number or has_phrase or "完全包含" in match_type:
                        sources.append(f"[{idx}] 《{filename}》{snippet}")
                        idx += 1
            
            # 如果过滤后只剩1个或0个，但原始有多个，说明过滤太严，放宽一点
            if len(sources) < 2 and len(unique_chunks) >= 2:
                # 取相关性最高的前2个（即使不完全匹配）
                for chunk in unique_chunks[:2]:
                    if len(sources) >= 2:
                        break
                    
                    # 检查是否已经在列表中（简单判断）
                    filename = chunk.metadata.get('filename', '未知文件')
                    already_added = any(filename in s for s in sources)
                    if already_added:
                        continue
                    
                    snippet = self._extract_relevant_snippet(chunk.content, answer, max_len=85)
                    if snippet and len(snippet) > 15:
                        # 标记为弱相关
                        sources.append(f"[{idx}] 《{filename}》[相关]{snippet}")
                        idx += 1
            
            # 最终保底：如果还是没有，只取第一个
            if not sources and unique_chunks:
                chunk = unique_chunks[0]
                filename = chunk.metadata.get('filename', '未知文件')
                snippet = self._extract_relevant_snippet(chunk.content, answer, max_len=85)
                if not snippet:
                    snippet = chunk.content[:70].replace('\n', ' ').strip()
                sources.append(f"[1] 《{filename}》{snippet[:80]}...")
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def list_documents(self) -> Dict[str, Any]:
        return self.vector_repo.list_documents()
