import socket
import selectors
import struct
import uuid
import sys
from src.User import User


class Server:
    def __init__(self):
        with open('port.info', 'r') as server_file:
            line = server_file.readline()
            self.port = int(line)
        self.host = '127.0.0.1'
        self.selector = selectors.DefaultSelector()
        self.version = 1
        self.users = {}
        self.error_response = struct.pack('B H I', self.version, 9000, 0)

    def accept(self, sock, mask):
        conn, address = sock.accept()  # Should be ready
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        try:
            data = conn.recv(1024)  # Should be ready

            if data:
                format_s = "<16s B B I {}s".format(len(data) - 22)
                client_id, version, code, size, payload = struct.unpack(format_s, data)

                # Register new User
                if code == 100:
                    response = self.register(str(payload, 'utf-8'))
                    conn.send(response)

                else:
                    # Check registered user
                    curr_uid = uuid.UUID(bytes=client_id)

                    # User not registered - return an error
                    if curr_uid not in self.users:
                        conn.send(self.error_response)

                    else:
                        # Return users list
                        if code == 101:
                            response = self.client_list(curr_uid)
                            print(response)
                            conn.send(response)

                        # Public key
                        elif code == 102:
                            response = self.public_key(uuid.UUID(bytes=payload))
                            conn.send(response)

                        # Send message
                        elif code == 103:
                            format_s = "16s B I {}s".format(size - 21)
                            other_client_id, m_type, m_size, m_content = struct.unpack(format_s, payload)
                            response = self.send_message(curr_uid, uuid.UUID(bytes=other_client_id),
                                                         m_type, m_size, m_content)
                            print(response)
                            conn.send(response)

                        # Return waiting messages
                        elif code == 104:
                            response = self.waiting_messages(curr_uid)
                            conn.send(response)

            else:
                self.selector.unregister(conn)
                conn.close()
        except:
            print("Unexpected error:", sys.exc_info())
            self.selector.unregister(conn)
            conn.close()

    def start(self):
        bind_socket = socket.socket()
        bind_socket.bind((self.host, self.port))
        bind_socket.listen()
        bind_socket.setblocking(False)
        self.selector.register(bind_socket, selectors.EVENT_READ, self.accept)

        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data

                callback(key.fileobj, mask)

    def register(self, user_name):
        # Check there is no user with same name
        for user in self.users.values():
            if user.name == user_name:
                return self.error_response

        new_user = User(user_name)
        self.users[new_user.id] = new_user
        return struct.pack('B H I 16s', self.version, 1000, 16, new_user.id.bytes)

    def client_list(self, requesting_user):
        payload = b""
        for user in self.users:
            if user != requesting_user:
                payload = b"".join([payload, self.users[user].get_user_bytes()])
        format_s = 'B H I {}s'.format(len(payload))
        return struct.pack(format_s, self.version, 1001, len(payload), payload)

    def public_key(self, user_uid):
        if user_uid not in self.users:
            return self.error_response

        other_user = self.users[user_uid]
        return struct.pack("B H I 16s 32s", self.version, 1002, user_uid.bytes, other_user.get_public_key())

    def waiting_messages(self, requesting_user_uid):
        user = self.users[requesting_user_uid]
        payload = user.get_waiting_messages_bytes()
        user.remove_waiting_messages()
        format_s = "B H I {}s".format(len(payload))
        return struct.pack(format_s, self.version, 1003, len(payload), payload)

    def send_message(self, from_user_uid, to_user_uid, m_type, m_size, m_content):
        if to_user_uid not in self.users:
            return self.error_response

        other_user = self.users[to_user_uid]
        message_id = other_user.add_message(from_user_uid, m_type, m_size, m_content)
        return struct.pack("B H I I", self.version, 1004, 4, message_id)
