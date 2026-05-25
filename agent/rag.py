from langchain_core.documents import Document
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from file_history_store import get_history
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from operator import itemgetter


def print_context(ctx):
    """打印检索到的参考资料（含文档元数据）"""
    print("=" * 40)
    print("【参考资料】")
    print(ctx)
    print("=" * 40)
    return ctx


def print_history(value):
    """打印历史对话记录"""
    history = value.get("history", [])
    print("=" * 40)
    print("【历史对话记录】")
    if not history:
        print("（无历史记录）")
    else:
        for msg in history:
            role = getattr(msg, "type", "unknown")
            content = getattr(msg, "content", str(msg))
            print(f"  [{role}] {content}")
    print("=" * 40)
    return value


def print_prompt(prompt):
    """打印最终构建的完整 prompt（含 System / History / User）"""
    print("=" * 40)
    print("【最终 Prompt】")
    for msg in prompt.messages:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        print(f"[{role}] {content}")
    print("=" * 40)
    return prompt

class RagService(object):
    def __init__(self):
        # 向量服务，用作检索
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name, dashscope_api_key=config.dashscope_api_key)
        )
        # 提示词
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system","以我提供的已知参考资料为主,"
                 "简洁和专业的回答用户问题，参考资料：{context}。"),
                ("system","并且我提供用户的对话历史记录，如下："),
                MessagesPlaceholder("history"),    #把历史数据history注入
                ("user","请回答用户提问：{input}")
            ]
        )
        self.chat_model = ChatTongyi(
            model=config.chat_model_name,
        )
        self.chain = self.__get_chain()
    
    def __get_chain(self):
        """获取最终的执行链"""
        retriever = self.vector_service.get_retriever()

        def format_document(docs:list[Document]):
            if not docs:
                print_context("没有相关资料")
                return "没有相关资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            print_context(formatted_str)
            return formatted_str
        
        #retriever要接受一个字符串对象，所以需要使用itemgetter将字典转化为字符串对象
        chain = (
            {
                "input" : itemgetter("input"),
                "context" : itemgetter("input") | retriever | format_document,
                "history": itemgetter("history"),
            }
            | self.prompt_template
            | self.chat_model
            | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )
 
        return conversation_chain

def print_session_history(session_id: str):
    """打印指定 session 的完整对话历史"""
    history = get_history(session_id).messages
    print("=" * 40)
    print("【历史对话记录】")
    if not history:
        print("（无历史记录）")
    else:
        for msg in history:
            role = getattr(msg, "type", "unknown")
            content = getattr(msg, "content", str(msg))
            print(f"  [{role}] {content}")
    print("=" * 40)


if __name__ == "__main__":
    # session id配置
    session_id = "user_001"
    session_config = {
        "configurable": {
            "session_id": session_id,
        }
    }
    res = RagService().chain.invoke({"input": "我身高170厘米，尺码推荐"}, session_config)
    print_session_history(session_id)
    print("【AI 回答】")
    print(res)
        