## Weller — 基于 RAG 的智能问答系统

本项目是一个基于 **RAG（检索增强生成）** 架构的问答系统，使用 **LangChain + Streamlit + ChromaDB** 构建，接入 **通义千问（Qwen）** 大模型，实现带知识库检索和多轮对话的智能尺码推荐。

---

### 核心功能

| 功能 | 说明 |
|---|---|
| **知识库上传** | 支持上传 `.txt` 文档，自动进行向量化并存储到本地 Chroma 向量库 |
| **智能问答** | 用户提问后，系统先检索知识库中的相关文档，再将检索结果与对话历史一并送入大模型生成回答 |
| **多轮对话** | 基于文件持久化的 `BaseChatMessageHistory`，每次对话自动保存历史上下文 |
| **Web 界面** | 使用 Streamlit 提供交互式聊天页面，支持文件上传、对话展示、一键清空 |

---

### RAG 流程

```text
用户提问
   │
   ▼
向量检索（ChromaDB + DashScope Embedding）
   │
   ▼
组装 Prompt：系统指令 + 参考资料 + 历史对话 + 当前问题
   │
   ▼
大模型生成回答（通义千问 ChatTongyi）
   │
   ▼
保存到对话历史 → 返回给用户

技术栈
Python 3.13
LangChain — RAG 链路编排、对话管理
Streamlit — Web 聊天界面
ChromaDB — 本地向量数据库
DashScope — 通义千问 Embedding 与 Chat 模型
File-based History — JSON 文件持久化多轮对话

项目结构
agent/
├── rag.py                 # RAG 核心链路（检索 + Prompt 组装 + LLM）
├── knowledge_base.py      # 知识库服务（文档向量化入库）
├── vector_stores.py       # Chroma 向量库封装
├── file_history_store.py  # 文件持久化聊天历史
├── app_qa.py              # Streamlit 主页面（聊天 + 文件上传）
├── config_data.py         # 配置项（模型名、API Key、分割参数等）
└── data/
    └── 尺码推荐.txt        # 示例知识库文档

快速开始
安装依赖

bash

插入到终端中

复制
pip install -r requirements.txt
配置 API Key（两种方式任选）

bash

插入到终端中

复制
# 方式一：环境变量
export DASHSCOPE_API_KEY="sk-你的通义千问APIKey"

# 方式二：在项目根目录创建 .env 文件
echo 'DASHSCOPE_API_KEY=sk-你的通义千问APIKey' > .env
启动 Web 服务

bash

插入到终端中

复制
streamlit run agent/app_qa.py
在浏览器打开页面，上传知识库文档后即可开始对话。
