import uuid
import struct
from src.Message import Message


class User:
    def __init__(self, connection, name, u_id=None, public_key=None, last_seen=None):
        self.connection = connection
        if u_id is None:
            u_id = uuid.uuid1()
        self.name = name
        self.id = u_id
        self.public_key = public_key
        self.last_seen = last_seen
        self.messages = []

    def get_user_bytes(self):
        user = struct.pack('16s 255s', self.id.bytes, bytes(self.name.ljust(255), 'utf-8'))
        return user

    def get_public_key(self):
        return self.public_key

    def add_message(self, sender, message_type, size, message):
        new_message = Message(sender, self.id, message_type, size, message)
        self.messages.append(new_message)
        return new_message.id
