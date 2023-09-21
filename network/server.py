import socket
import time


class PlayerOneLeft(Exception):  # special exception when player one leaves the game
    pass


class Server:

    HOST = 'localhost'
    PORT = 49550

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4, tcp
        self.socket.bind((Server.HOST, Server.PORT))  # binding socket to address and port
        self.conn1 = self.conn2 = self.address1 = self.address2 = None
        self.connect()

    def connect(self):
        self.socket.listen()  # wait for socket to connect
        self.conn1, self.address1 = self.socket.accept()  # conn1 and address1 are the info of the first socket
        self.conn1.sendall(b'W')  # give the first client color W
        self.socket.listen()  # wait for second client to connect
        self.conn2, self.address2 = self.socket.accept()  # conn2 and address2 are the info of the second socket
        try:
            x = self.conn1.recv(1000).decode('UTF-8')  # check if the first player is still connected
        except ConnectionResetError:
            self.conn2.send(b'Q')  # tell second client that the first player left
            raise PlayerOneLeft()
        if 'Q' in x:
            raise PlayerOneLeft()
        self.conn2.sendall(b'B')  # if everything worked, second client is black
        self.conn1.sendall(b'2')  # telling player 1 that the game started
        time.sleep(0.1)  # wait so that the messages won't be sent as one
        self.conn2.sendall(b'2')  # telling player 2 that the game started
        self.send()

    def send(self):  # transfer information between the clients
        while True:
            try:
                self.conn2.sendall(self.conn1.recv(1000))
                self.conn1.sendall(self.conn2.recv(1000))
            except (ConnectionResetError, ConnectionAbortedError, OSError):  # if one of the players leaves,
                # stop loop and close
                self.socket.close()
                return


if __name__ == "__main__":
    print('Server Initiated.')
    try:
        server = Server()
    except PlayerOneLeft:
        print('Server shutting down because a player left before the game began. Please start over.')
    print('Server Closed.')
