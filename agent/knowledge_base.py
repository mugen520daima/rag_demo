"""
知识库
"""
import os
from . import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

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
            embedding_function=DashScopeEmbeddings(model_name="text-embedding-v4") ,
            persist_directory=config.persist_directory
        ) #向量存储的实例 Chroma向量库对象
        self.spliter = None #文本分割器的对象

    def upload_by_str(self,data,filename):
        #将传入的字符串，进行向量化，存入向量化数据库中
        pass