
md5_path = "./md5.text" 

# Chroma
collection_name = "rag"
persist_directory = "./chroma_db"

# spliter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", " ", ",", ".", "!", ";", "?", "","。"]

# 文本超过这个阈值才进行分割，否则不进行分割
max_split_char_number = 1000