"""
知识库
"""
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str):
    """检查传入的md5字符串是否已经被处理过"""
    # 如果md5文件不存在，则创建空文件并返回False（表示未处理过）
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w',encoding='utf-8').close()
        return False;
    else:
        # 读取md5文件，逐行检查是否已存在该md5值
        for line in open(config.md5_path,'r',encoding='utf-8').readlines():
            line = line.strip()
            if line == md5_str:
                return True  # 找到匹配的md5，返回True表示已处理过
        return False  # 文件中未找到该md5，返回False

def save_md5(md5_str):
    """保存md5字符串到文件中"""
    with open(config.md5_path,'a',encoding='utf-8') as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str,encoding='utf-8'):
    """获取字符串的md5值"""
    str_bytes = input_str.encode(encoding=encoding)

    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest()
    return md5_hex

class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name, #数据库的表名
            embedding_function=DashScopeEmbeddings(
                model="text-embedding-v1",
                dashscope_api_key=config.dashscope_api_key
            ),
            persist_directory=config.persist_directory
        ) #向量存储的实例 Chroma向量库对象
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  #分割后的文本段的最大长度
            chunk_overlap=config.chunk_overlap,  #相邻文本块之间的重叠字符数，防止上下文丢失
            separators=config.separators, #按照列表的元素进行文本切割
            length_function=len, #计算文本长度的函数
        ) #文本分割器的对象

    def upload_by_str(self,data : str,filename):
        #将传入的字符串，进行向量化，存入向量化数据库中
        # 首先先得到传入字符串的md5值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"
        if len(data) > config.max_split_char_number:
            knowledge_chunks     = self.spliter.split_text(data)
        else:
            knowledge_chunks     = [data]
        
        # 定义元数据字典，存储与文本块关联的附加信息
        metadata = {
            "source" : filename, #	来源文件名，记录这段文本来自哪个文件
            "create_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "weller",
        }
        self.chroma.add_texts(   # 内容加载到向量库
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks], #为每个文本块关联对应的元数据
        )
        save_md5(md5_hex) 
        return "[成功]内容添加到知识库中" 

if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("测试字符串", "testfile")
    print(r)