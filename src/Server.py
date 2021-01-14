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
                    new_user = User(conn, str(payload, 'utf-8'))
                    self.users[new_user.id] = new_user
                    response = struct.pack('B H I 16s', self.version, 1000, 16, new_user.id.bytes)
                    conn.send(response)

                else:
                    # Check registered user
                    curr_uid = uuid.UUID(bytes=client_id)

                    # User not registered - return an error
                    if curr_uid not in self.users:
                        response = struct.pack('B H I', self.version, 9000, 0)
                        print(response)
                        conn.send(response)

                    else:
                        # Return users list
                        if code == 101:
                            payload = b""
                            for user in self.users:
                                if user != curr_uid:
                                    payload = b"".join([payload, self.users[user].get_user_bytes()])
                            format_s = 'B H I {}s'.format(len(payload))
                            response = struct.pack(format_s, self.version, 1001, len(payload), payload)
                            conn.send(response)

                        # Public key
                        elif code == 102:
                            other_user_uid = uuid.UUID(bytes=payload)

                            # TODO: add exception
                            if other_user_uid in self.users:
                                other_user = self.users[other_user_uid]
                                response = struct.pack("B H I 16s 32s", self.version, 1002, other_user_uid.bytes,
                                                       other_user.get_public_key())
                                print(response)
                                conn.send(response)

                        # Send message
                        elif code == 103:
                            format_s = "16s B I {}s".format(size - 21)
                            other_client_id, m_type, m_size, m_content = struct.unpack(format_s, payload)
                            other_user_uid = uuid.UUID(bytes=other_client_id)

                            # TODO: add exception
                            if other_user_uid in self.users:
                                other_user = self.users[other_user_uid]
                                message_id = other_user.add_message(curr_uid, m_type, m_size, m_content)
                                response = struct.pack("B H I I", self.version, 1004, 4, message_id)
                                print(response)
                                conn.send(response)

                        # Return waiting messages
                        elif code == 104:
                            user = self.users[curr_uid]
                            payload = user.get_waiting_messages_bytes()
                            format_s = "B H I {}s".format(len(payload))
                            response = struct.pack(format_s, self.version, 1003, len(payload), payload)
                            print(response)
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
