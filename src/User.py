import uuid
import struct
from src.Message import Message


class User:
    def __init__(self, name, public_key, u_id=None, last_seen=None):
        if u_id is None:
            u_id = uuid.uuid1()
        self.name = name
        self.id = u_id
        self.public_key = public_key
        self.last_seen = last_seen
        self.messages = []
        self.next_message_id = 1

    def get_user_bytes(self):
        user = struct.pack('16s 255s', self.id.bytes, bytes(self.name.ljust(255, '\0'), 'utf-8'))
        return user

    def add_message(self, sender, message_type, size, message):
        new_message = Message(self.next_message_id, self.id, sender, message_type, size, message)
        self.next_message_id += 1
        self.messages.append(new_message)
        return new_message.id

    def get_waiting_messages_bytes(self):
        m_list = b""
        for message in self.messages:
            m_list = b"".join([m_list, message.get_message_bytes()])
        return m_list

    def remove_waiting_messages(self):
        self.messages.clear()
