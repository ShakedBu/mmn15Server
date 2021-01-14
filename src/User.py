import uuid
import struct


class User:
    def __init__(self, connection, name, u_id=None, public_key=None, last_seen=None):
        self.connection = connection
        if u_id is None:
            u_id = uuid.uuid1()
        self.name = name
        self.id = u_id
        self.public_key = public_key
        self.last_seen = last_seen

    def get_user_bytes(self):
        # TODO: this will probably wont work
        user = struct.pack('16s 255s', self.id.bytes, bytes(self.name.ljust(255), 'utf-8'))
        return user
