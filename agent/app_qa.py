"""
Weller衣服尺码推荐器
streamlit run /Users/weller/ComateProjects/comate-zulu-demo-1779097104501/agent/app_qa.py

运行：
cd /Users/weller/ComateProjects/comate-zulu-demo-1779097104501
export DASHSCOPE_API_KEY="sk-b8b26a2aad944b3fafe0ec00eb2de824"
.venv/bin/streamlit run agent/app_qa.py
"""
import uuid
import streamlit as st
from rag import RagService
from knowledge_base import KnowledgeBaseService

st.set_page_config(page_title="Weller衣服尺码推荐器", page_icon="👔")

st.title("👔 Weller衣服尺码推荐器")
st.markdown("基于知识库的RAG智能尺码推荐，支持多轮对话")

# ---------- 侧边栏：文件上传 ----------
with st.sidebar:
    st.header("📁 知识库管理")
    uploaded_file = st.file_uploader("上传尺码文档（.txt）", type=["txt"])

    if "kb_service" not in st.session_state:
        st.session_state["kb_service"] = KnowledgeBaseService()

    if uploaded_file is not None:
        text = uploaded_file.getvalue().decode("utf-8")
        st.text_area("文件预览", text, height=200)
        if st.button("加载到知识库"):
            with st.spinner("正在向量化..."):
                res = st.session_state["kb_service"].upload_by_str(text, uploaded_file.name)
            st.success(res)

    st.divider()
    if st.button("🗑️ 清空当前对话"):
        st.session_state["messages"] = []
        st.session_state["session_id"] = uuid.uuid4().hex
        st.rerun()

# ---------- 初始化 RAG 服务 ----------
if "rag_service" not in st.session_state:
    st.session_state["rag_service"] = RagService()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4().hex

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------- 展示历史消息 ----------
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- 用户输入 ----------
user_input = st.chat_input("请输入您的问题，例如：我身高170厘米，尺码推荐")

if user_input:
    # 显示用户消息
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 调用 RAG 链
    session_config = {"configurable": {"session_id": st.session_state["session_id"]}}
    with st.spinner("正在思考..."):
        try:
            response = st.session_state["rag_service"].chain.invoke(
                {"input": user_input}, session_config
            )
        except Exception as e:
            response = f"调用出错：{e}"

    # 显示 AI 回复
    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
