import socket


class Player_Client:

    HOST = 'localhost'
    PORT = 49550

    def __init__(self, game):
        self.main = game  # self.main.client = self
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close(self):
        self.socket.close()

    def con(self):  # connect to server
        self.socket.connect((Player_Client.HOST, Player_Client.PORT))  # connect to host, server
        self.color = self.socket.recv(8).decode('UTF-8')  # color of player received by server
        self.socket.recv(1024)  # wait for signal that the game started
        self.main.connected = True  # inform main that connection has been established

    def request(self):  # receive info from server through socket and append to main's queue
        self.main.que.append(self.socket.recv(1000).decode('UTF-8'))

    def send(self, info):  # send info to server through socket
        self.socket.send(info.encode('UTF-8'))
