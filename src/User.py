import uuid
import struct


class User:
    def __init__(self, name, u_id=None, public_key=None, last_seen=None):
        if u_id is None:
            u_id = uuid.uuid1()
        self.name = name
        self.id = u_id
        self.public_key = public_key
        self.last_seen = last_seen

    def get_user_bytes(self):
        format_s = '16s {}s'.format(len(self.name))
        user = struct.pack(format_s, self.id.bytes, self.name)
        return user
