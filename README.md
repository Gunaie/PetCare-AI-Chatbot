\---

title: PetCare AI Chatbot

emoji: 🐱🐶🐰

colorFrom: purple

colorTo: blue

sdk: docker

pinned: false

\---



\# PetCare AI Chatbot



基于 RAG（检索增强生成）的宠物护理知识库问答系统。



\## 核心功能



\- 📚 \*\*文档上传\*\*：支持 PDF/TXT 批量上传，自动 OCR 识别扫描件

\- 🔍 \*\*智能检索\*\*：基于 BAAI/bge-m3 向量模型语义检索

\- 💬 \*\*安全问答\*\*：DeepSeek LLM 生成答案，强制添加医疗免责声明

\- ⚠️ \*\*来源追溯\*\*：所有答案标注参考文档来源



\## 技术栈



\- FastAPI + Uvicorn

\- ChromaDB 向量数据库

\- Sentence-Transformers (bge-m3)

\- DeepSeek API

\- PaddleOCR



\## 使用方式



1\. 在"上传知识库"区域拖拽或点击上传宠物护理文档（PDF/TXT）

2\. 在"宠物知识问答"输入框提问，如"幼猫什么时候打疫苗？"

3\. 查看答案和参考来源



\## 安全提示



⚠️ 本系统所有回答均包含免责声明：\*\*宠物健康问题请务必咨询专业兽医\*\*。

