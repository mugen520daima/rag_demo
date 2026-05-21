from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from agent.file_history_store import get_history
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
import config_data as config
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from pydantic import SecretStr



def print_prompt(prompt):
    print("***")
    print(prompt)
    print("***")

    return prompt

class RagService(object):
    def __init__(self):
        # 向量服务，用作检索
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )
        # 提示词
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system","以我提供的已知参考资料为主,"
                 "简洁和专业的回答用户问题，参考资料：{context}。"),
                ("system","并且我提供用户的对话历史记录，如下："),
                MessagesPlaceholder("histrory"),    #把历史数据history注入
                ("user",f"请回答用户提问：{input}")
            ]
        )
        self.chat_model = ChatTongyi(
            model=config.chat_model_name,
            api_key=SecretStr(config.api_key) 
        )
        self.chain = self.__get_chain()
    
    def __get_chain(self):
        """获取最终的执行链"""
        retriever = self.vector_service.get_retriever()

        def format_document(docs:list[Document]):
            if not docs:
                return "没有相关资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n" 
            return formatted_str
        
        chain = (
            {
                "input" : RunnablePassthrough(),
                "context" : retriever | format_document
            } | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
        )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        return conversation_chain

if __name__ == "__main__":
    res = RagService().chain.invoke("我身高170厘米，尺码推荐")
    print(res)
        