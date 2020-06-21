import socket


class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.56.1" # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                # ipv4 address. This feild will be the same for all your clients.
        self.port = 5555
        self.addr = (self.host, self.port)
        # HANDLE HANDSHAKE HERE HERE
        self.id = int(self.connect())

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(2048).decode()

    def send(self, data):

        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            # print(reply)
            return reply
        except socket.error as e:
            return str(e)
