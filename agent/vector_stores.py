from langchain_chroma import Chroma
import config_data as config

#sk-b7840b7b2fb24e51a2d31c79f3b087f3

class VectorStoreService(object):
    def __init__(self,embedding):
        """
        embedding: 嵌入模型的传入
        """
        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory
        )
    
    def get_retriever(self):
        """
        返回向量检索器，方便加入chain中
        """
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})  #表示返回2个匹配的向量检索器


if __name__ == "__main__":
    from langchain_community.embeddings import DashScopeEmbeddings
    vs = VectorStoreService(DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=config.dashscope_api_key
    )).get_retriever()

    res = vs.invoke(input="我的体重180斤，尺码推荐")
    print(res)