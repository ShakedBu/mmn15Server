import socket
import selectors
import struct
import uuid
from src.User import User


class Server:
    def __init__(self):
        with open('port.info', 'r') as server_file:
            line = server_file.readline()
            self.port = int(line)
        self.host = '127.0.0.1'
        self.selector = selectors.DefaultSelector()
        self.users = []

    def accept(self, sock, mask):
        conn, address = sock.accept()  # Should be ready
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        data = conn.recv(1024)  # Should be ready
        print(data)

        if data:
            format_s = "<16s B B I {}s".format(len(data) - 22)
            client_id, version, code, size, payload = struct.unpack(format_s, data)
            print(client_id, version, code, payload)

            # Register new User
            if code == 100:
                new_user = User(repr(payload))
                self.users.append(new_user)
                response = struct.pack('B H I 16s', 1, 1000, 16, new_user.id.bytes)
                conn.send(response)
            else:
                # Check registered user

                # Return users list
                if code == 101:
                    uid = uuid.UUID(bytes=client_id)
                    # TODO: Check if there is such user and get him a list

                    pass
                # Public key
                elif code == 102:
                    pass
                # Send message
                elif code == 103:
                    pass
                # Return waiting messages
                elif code == 104:
                    pass

        else:
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
