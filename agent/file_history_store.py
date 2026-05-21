from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, message_to_dict, messages_from_dict
from typing import Sequence, override
import os
import json
from datetime import datetime

def get_history(session_id):
    return FileChatMessageHistory(session_id,'./chat_history')

class FileChatMessageHistory(BaseChatMessageHistory):
    """基于文件的聊天历史记录管理，用于长期会话记忆"""

    def __init__(self, session_id, storage_path):
        """
        初始化文件聊天历史记录

        Args:
            session_id: 会话ID，用于区分不同会话
            file_dir: 聊天历史存储目录
        """
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path,self.session_id)

        # 确保目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self,messages: Sequence[BaseMessage]):
        # Sequence序列 类似list、tuple
        all_messages = list(self.messages)      # 已有的消息列表
        all_messages.extend(messages)           # 新的和已有的融合成一个list
        """
        将数据同步写入到本地文件中
        类对象写入文件 -> 一堆二进制
        为了方便，可以将BaseMessage消息转为字典（借助json模块以json字符串写入文件）
        官方message_to_dict: 单个消息对象（BaseMessage类实例） -> 字典
        new_messages = []
        for message in all_messages:
        d = message_to_dict(message)
        new_messages.append(d)
        """
        new_messages = [message_to_dict(message) for message in all_messages]
        # 将数据写入文件
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f)


    @property    # @property装饰器，将message方法变成成员属性使用
    @override
    def messages(self) -> list[BaseMessage]:
        # 当前文件内： list[字典]
        try:
            with open(self.file_path,"r",encoding="utf-8") as f:
                messages_data = json.load(f)  #返回值就是：list[字典]
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
    
    def clear(self):
        with open(self.file_path,"w",encoding="utf-8") as f:
            json.dump([],f)