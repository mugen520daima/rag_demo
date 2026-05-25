import os
from dotenv import load_dotenv
load_dotenv()

md5_path = "./md5.text"

# DashScope API Key
dashscope_api_key = os.environ.get("DASHSCOPE_API_KEY", "")

# Chroma
collection_name = "rag"
persist_directory = "./chroma_db"

# spliter
chunk_size = 100
chunk_overlap = 100
separators = ["\n\n", "\n", " ", ",", ".", "!", ";", "?", "","。"]

# 文本超过这个阈值才进行分割，否则不进行分割
max_split_char_number = 100

# 检索返回匹配的文档数量
similarity_threshold = 1

embedding_model_name = "text-embedding-v1"
chat_model_name = "qwen3-max"
api_key = os.environ.get("DASHSCOPE_API_KEY", "")