import struct


class Message:
    def __init__(self, to_client, from_client, m_type, m_size, content):
        # TODO: Generate message id
        self.id = 1
        self.to_client = to_client
        self.from_client = from_client
        self.type = m_type
        self.content = content
        self.size = m_size

    def get_message_bytes(self):
        format_s = "I B I {}s".format(self.size)
        message = struct.pack(format_s, self.id, self.type, self.size, bytes(self.content))
        return message
