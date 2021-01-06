import socket
import ssl


class Server:
    def __init__(self):
        with open('port.info', 'r') as server_file:
            line = server_file.readline()
            self.host = line
        self.host = '127.0.0.1'

    def start(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="mycertfile", keyfile="mykeyfile")

        bind_socket = socket.socket()
        bind_socket.bind((self.host, self.port))
        bind_socket.listen(5)

        while True:
            new_socket, from_addr = bind_socket.accept()
            conn_stream = context.wrap_socket(new_socket, server_side=True)
            try:
                self.deal_with_client(conn_stream)
            finally:
                conn_stream.shutdown(socket.SHUT_RDWR)
                conn_stream.close()

    def deal_with_client(self, conn_stream):
        data = conn_stream.recv(1024)
        # empty data means the client is finished with us
        while data:
            #if not do_something(conn_stream, data):
                # we'll assume do_something returns False
                # when we're finished with client
            #    break
            data = conn_stream.recv(1024)
        # finished with client


if __name__ == '__main__':
    message_u = Server()
    message_u.start()
