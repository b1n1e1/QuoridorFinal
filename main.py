import pygame
import pygame.gfxdraw
import collections
import sys
from quoridor.constants import *
from quoridor.game import Game
from ai.algorithm import AI
from network.client import Player_Client
from threading import Thread
import time


class Main:

    SCREENS = [pygame.image.load('Quoridor-Pick Mode.png'), pygame.image.load('Quoridor-Local.png'),
               pygame.image.load('Quoridor-Multiplayer wait.png'), pygame.image.load('Quoridor-AI.png'),
               pygame.image.load('Quoridor-Rules.png'), pygame.image.load('White wins.png'),
               pygame.image.load('Black wins.png')]  # list of all images shown throughout game.

    def __init__(self, typ):
        pygame.init()
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # creates pygame display as main window
        pygame.display.set_caption('Quoridor')
        self.game = Game(False)  # self.game is a game which isn't initiated yet
        self.type = typ  # type of game. 1: local, 2: online 3: vs ai
        self.ai = AI()  # AI engine, set as default value
        self.game_stack = []  # stack of all games
        self.winners = {BLACK:self.black_wins, WHITE:self.white_wins,'W':self.black_wins, 'B':self.white_wins}
        # key to function to save pointless if statements. 'W' calls to black wins and vice versa because it will be
        # called when that color forfeits.

    def black_wins(self):
        """
        Display screen "black wins"
        """
        time.sleep(0.2)
        print('Black wins.')
        self.WIN.blit(self.SCREENS[6], (0, 0))
        pygame.display.update()
        time.sleep(1)

    def white_wins(self):
        """
        Display screen "white wins"
        :return:
        """
        time.sleep(0.2)
        print('White wins.')
        self.WIN.blit(self.SCREENS[5], (0,0))
        pygame.display.update()
        time.sleep(1)

    def ai_move(self):
        """
        Do move for AI
        """
        temp = self.game.turns  # to save the amount of turns
        self.game = self.ai.do(self.game)
        self.game.turns = temp + 1  # correct amount of turns
        self.game.select((0, 0))  # deselect piece

    def wait(self):
        screen = self.SCREENS[0]  # opening screen
        self.WIN.blit(screen, (0, 0))
        while self.type == 0:  # while no type has been selected
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.type = 4  # close screen
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_1:  # local multiplayer
                        self.type = 1
                    if event.key == pygame.K_2:  # online multiplayer
                        self.type = 2
                    if event.key == pygame.K_3:  # against ai
                        self.type = 3
                    if event.key == pygame.K_SPACE:  # show rules
                        self.WIN.blit(self.SCREENS[4], (0, 0))
                    if event.key == pygame.K_ESCAPE:  # close rules
                        self.WIN.blit(self.SCREENS[0], (0, 0))
                if event.type == pygame.MOUSEBUTTONUP:  # close rules
                    self.WIN.blit(self.SCREENS[0], (0, 0))

    @timeit  # print time game was running in the end
    def main(self):
        """
        Game
        """
        self.wait()  # while the player hasn't selected the mode, show loading screen.
        if self.type == 4:  # if player closed the game in self.wait
            return
        if self.type == 2:
            self.multi()
            return
        run = True
        undo_clicked = [1,1,True] if self.type == 1 else [1,0,True]
        """each human player can undo once throughout game. When undo_clicked[2] = True, undo can't be clicked
         (first turn or if ctrl z is already pressed)"""
        while run:
            screen = self.SCREENS[self.type]  # 1 if local multiplayer, 3 if AI
            if not self.game.started:  # while game hasn't been initiated
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # close screen
                        run = False
                    if event.type == pygame.MOUSEBUTTONUP and self.type == 1:  # start local game when screen is clicked
                        self.game.init()
                        self.game_stack.append(Game())  # add initial game to stack for undo
                    if self.type == 3:
                        if event.type == pygame.KEYUP:  # set up AI based on number clicked
                            typ = pygame.key.name(event.key)
                            try:
                                self.ai = AI(int(typ))
                            except ValueError:  # a string or incorrect number was entered
                                pass  # the ai is the default
                            self.game.init()
                            self.game_stack.append(Game())  # the first item in the game stack is the initial game
                self.WIN.blit(screen, (0,0))
                pygame.display.update()
            else:
                if self.game.turns > 13 and not self.game.checked_for_winner:  # check for winner only when turn starts
                    win = self.game.winner()
                    if win:  # and only if its technically possible for there to be a winner (14 turns)
                        self.winners[win]()
                        break
                    self.game.checked_for_winner = True
                if self.type == 1 or self.game.turn==WHITE:  # if a human player is playing
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:  # if the game was closed
                            self.winners[tuple(255-i for i in self.game.turn)]()  # display player who didn't quit
                            run = False

                        if event.type == pygame.MOUSEBUTTONUP:  # select tile
                            pos = pygame.mouse.get_pos()
                            temp = self.game.turns
                            self.game.select(pos)
                            if self.game.turns > temp and any(undo_clicked[0:2]):  # if the turn has changed
                                self.game_stack.append(self.game.clone())  # and undo hasn't been used by both players
                                self.game_stack[-1].turns = self.game.turns
                                undo_clicked[2] = False

                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_SPACE:  # lift wall
                                [self.game.lift_wall, self.game.unlift][self.game.wall_selected['sel']]()  # lift if not
                                # lifted, don't lift if lifted
                            if event.key == pygame.K_f:  # flip wall
                                self.game.flip()
                            if event.key == pygame.K_z and self.game.turns > 0:
                                undo_clicked[2] = False
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LCTRL] and keys[pygame.K_z] and \
                            undo_clicked[self.game.turn==BLACK] and not undo_clicked[2]:  # if ctrl z has been clicked
                        self.game_stack.pop()  # and the current player can undo
                        self.game = self.game_stack[-1]
                        undo_clicked[self.game.turn==WHITE] = 0
                        print(f'{"White" if self.game.turn == WHITE or self.type == 3 else "Black"} undid turn.')
                        undo_clicked[2] = True
                        if self.type == 3:  # undo black and white move in case of AI
                            self.game_stack.pop()
                            self.game = self.game_stack[-1]

                elif run and self.type == 3:  # it's ai's turn
                    self.ai_move()
                    if undo_clicked[0]:
                        self.game_stack.append(self.game.clone())
                        self.game_stack[-1].turns = self.game.turns

                if run:
                    self.game.update(self.WIN, pygame.mouse.get_pos())  # always update the screen

    def connect(self):
        """
        Create client object with main object and connect to server. If connection fails, catch exception.
        """
        self.client = Player_Client(self)  # self.client -> client object. client.main -> self
        try:
            self.client.con()  # connect to server
        except (ConnectionAbortedError, ConnectionRefusedError, TimeoutError):
            return  # if unable to connect to server, do nothing.

    def client_listen(self):
        """
        Function that will always be running in the second thread, fills self.que with TCP values.
        """
        while self.playing:
            try:
                self.client.request()
            except ConnectionResetError:  # the connection has been closed - TCP RST received
                self.playing = False
                self.client.close()
            except ConnectionAbortedError:  # the connection has been forced to close due to exception
                return

    def multi(self):
        """
        Multiplayer Game.
        """
        self.que = collections.deque()  # queue that will save all of the received messages
        self.connected = False  # will be true when the other thread will connect to the server
        self.playing = True  # will be false when the game is over / aborted. used to communicate between the threads
        Thread(target=self.connect).start()  # thread to connect to server while screen loads
        self.WIN.blit(self.SCREENS[2], (0,0))
        time.sleep(0.5)  # wait for other thread to finish
        try:
            self.client.send('hello!')  # try to send message to server
        except OSError:  # raised if there's no server
            print("Server hasn't been opened yet.")
            return
        while not self.connected and self.playing:
            try:
                self.client.color  # see if the server sent a color or if it's currently running a different game.
            except AttributeError:  # self.client doesnt have the attribute color because it's stuck on recv(8) in con
                print('A game is currently taking place. Please wait until the current game ends.')
                self.client.close()
                return
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # X has been clicked while waiting for other player to connect
                    self.playing = False
                    self.client.send('Q')
                    self.client.close()
            pygame.display.update()
        self.game.init()  # start game
        run = True  # for game loop
        Thread(target=self.client_listen).start()  # start constant listening
        turns = {BLACK:'B', WHITE:'W'}  # (0,0,0):'B", (255,255,255):'W"
        if self.client.color == 'Q':  # if the other player left before the game started
            print('The white player has left the game.')
            self.black_wins()
            return
        print(f"You are {'Black' if self.client.color=='B' else 'White'}.")  # prints on screen player's color
        wall_selected_multi = False  # boolean to draw wall on board while the wall is lifted
        while run:
            if not self.playing:  # if the other thread stopped
                return
            if self.game.turns > 13 and not self.game.checked_for_winner:  # if it's possible for there to be a winner
                win = self.game.winner()
                if win:
                    self.winners[win]()
                    self.playing = False
                    self.client.close()
                    break
                self.game.checked_for_winner = True  # there's no winner. wait until next move and don't check again
            if turns[self.game.turn] == self.client.color:  # if it's the player's turn
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # if X was clicked
                        print('You forfeit.')
                        self.client.send('Q')  # let other client know that game is over
                        self.winners[self.client.color]()
                        self.client.close()
                        return
                    if event.type == pygame.MOUSEBUTTONUP:  # screen was clicked
                        ms = pygame.mouse.get_pos()
                        legal = self.game.select(ms)
                        if legal != 'illegal':  # if the move was legal
                            st = f"S{ms[0]:3d},{ms[1]:3d}"  # send coordinates to other player, always length 8
                            wall_selected_multi = False  # for updating screen
                            self.client.send(st)
                        else:
                            self.client.send('L')
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            self.game.lift_wall()
                            wall_selected_multi = True
                            self.client.send('L')
                        if event.key == pygame.K_f:
                            self.game.flip()
                            self.client.send('F')
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print('You forfeit.')
                        self.client.send('Q')
                        self.winners[self.client.color]()
                        self.client.close()
                        return

            self.game.update(self.WIN, pygame.mouse.get_pos() if wall_selected_multi else None, self.client.color)
            self.client.send('0')  # send stream of data at all times
            if len(self.que) > 0:  # if the request queue has data
                received = self.que.popleft()  # get earliest message
                place = received.find('S')  # if message contains S, returns position of s, else return -1
                if place != -1:  # if message contains S
                    self.game.select((int(received[place+1:place+4]), int(received[place+5:place+8])))  # select at pos
                if 'L' in received:  # if other player lifted wall
                    self.game.lift_wall()
                if 'F' in received:  # if other player flipped wall
                    self.game.flip()
                if 'Q' in received:
                    self.playing = False
                    print('The other player has left the game.')
                    self.winners[{'B':BLACK, 'W':WHITE}[self.client.color]]()
                    return
        return 0


if __name__ == '__main__':
    try:
        x = int(sys.argv[1])
    except (IndexError, ValueError):
        x = 0
    create = Main(x)
    create.main()
