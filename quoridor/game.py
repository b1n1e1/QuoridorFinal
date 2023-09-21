from .board import Board
from .pieces import *


class Game:
    """
    Game class
    """
    def __init__(self, init=True):
        if init:
            self.init()
        else:
            self.started = False

    def init(self):
        """
        Start game (or reset)
        """
        self.started = True
        self.turns = 0
        self.checked_for_winner = False
        self.selected = None  # No tile is selected
        self.wall_selected = {'sel':False, 'dir':1}  # No wall is lifted
        self.turn = WHITE  # First turn is WHITE
        self.board = Board()  # Create board
        self.winner = lambda: self.board.winner()  # Returns winner (None if no one is winning)
        self.valid_moves = set()  # Set of valid moves for selected piece (currently empty because no piece is selected)
        self.walls_remaining = [WALLS,WALLS]  # First is player 1, second is player 2. Walls left for each player

    def clone(self):
        """
        Creates a copy of the game

        :return: Copy
        """
        new_game = Game()
        new_game.turn = self.turn
        new_game.board = self.board.clone()
        new_game.walls_remaining = [*self.walls_remaining]
        return new_game

    def place(self, pos):
        """
        Place a wall at position pos on board

        :param pos: Position on board
        :return: True if wall is placed
        """
        x = self.turn == BLACK  # x=0/False if turn is white and 1/True if turn is black
        if self.board.can_place((pos, self.wall_selected['dir'])):  # If the placement isn't intercepting another wall
            self.board.place_wall((pos,self.wall_selected['dir']))  # Place the wall in pos
            self.walls_remaining[x] -= 1
            self.wall_selected['dir'] = 1
            self.next_turn()
            return True  # Wall was successfully placed
        return False

    def place_ai(self, pos, dir):
        x = self.turn == BLACK
        self.board.place_wall((pos, dir))
        self.walls_remaining[x] -= 1
        self.next_turn()

    def flip(self):
        """
        Flip selected wall. Does nothing if no wall is selected
        """
        if self.wall_selected['sel']:
            self.wall_selected['dir'] = 1 - self.wall_selected['dir']

    def select(self, pos):
        """
        Select tile in pos

        :param pos: Given x,y position of selected section
        :return: True if worked, False if not
        """
        board_pos = (pos[0] // TILE_WIDTH, (pos[1] - MARGIN) // TILE_HEIGHT)
        if self.wall_selected['sel']:  # If a wall is being placed by a human player
            board_pos = (round(pos[0]/TILE_WIDTH), round((pos[1] - MARGIN) / TILE_HEIGHT))  # Closest position to mouse
            placed = self.place(board_pos)
            if not placed:  # If failed to place a wall
                self.wall_selected['sel'] = False
                print('Illegal Move')
                return 'illegal'
            return True
        elif self.selected:  # If a piece is currently selected
            result = self.move(board_pos)  # Try to move the currently selected piece to the pos
            if not result:  # If unable to move the piece
                self.selected = None  # Unselect piece
                self.valid_moves = set()  # No piece selected so no possible moves
                self.select(pos)  # Select the new tile that was clicked.
            return result

        if board_pos[1] > ROWS-1 or board_pos[0] > ROWS-1:
            return False  # If selected beyond range, return False
        piece = self.board.get_piece(board_pos)  # Piece at tile that was selected (if no piece, piece=0)

        if piece != 0 and piece.color == self.turn:
            self.selected = piece  # Next time the board is clicked, the select function will run on this piece
            self.valid_moves = self.board.possible_moves()[(piece.pos[0], piece.pos[1])]  # Update valid moves
            return True  # The piece has been successfully selected
        return False  # No piece has been selected

    def move(self, pos):
        """
        Move piece

        :param pos: Position which the selected piece (self.selected) will be moving to
        :return: True if piece was able to move according to rules, false otherwise
        """
        if pos[1]>ROWS-1 or pos[0]>ROWS-1:  # If pos is above or below the board
            return False  # Can't move the piece above the board or under, return false

        piece = self.board.get_piece(pos)  # Needs to be 0, if not then the piece cannot move to the given place
        if self.selected and piece == 0 and pos in self.valid_moves:
            self.board.move(self.selected, pos)  # Move the selected piece to the pos if it's a valid move
            self.next_turn()
        else:
            return False  # Unable to move piece, return False
        return True  # Piece successfully moved

    def next_turn(self):
        """
        Reset the selections and change the turn
        """
        self.valid_moves = set()  # There are no valid moves because no pawn has been selected
        self.wall_selected['sel'] = False  # Unselect any walls when changing turns
        self.turn=BLACK if self.turn==WHITE else WHITE
        self.turns += 1
        self.checked_for_winner = False

    def draw_moves(self, win):
        """
        Draw all possible moves for selected pawn.

        :param win: Game window
        """
        for move in self.valid_moves:
            row, col = move
            pygame.gfxdraw.aacircle(win, row*TILE_WIDTH + TILE_WIDTH // 2,
                                    col*TILE_HEIGHT + TILE_HEIGHT // 2 + MARGIN, MOVE_RADIUS, GRAY)

    def walls_left(self, win, color=None):
        """
        Writes in margins how many walls are left for each player

        :param win: Game window
        :param color: If the game is multiplayer, color is the color of the client
        """
        for i in range(2):
            n = FONT.render(f'{self.walls_remaining[i]} walls left.', True, BLACK)
            w, h = n.get_size()
            win.blit(n, ((WIDTH - w) // 2, (MARGIN + BOARD_HEIGHT) * (1 - i) + (MARGIN - h) // 2))  # writing on center
        if color:
            if self.turn == BLACK and color == 'B' or self.turn == WHITE and color == 'W':
                n = SMALL_FONT.render("Your turn.", True, BLACK)
            else:
                n=SMALL_FONT.render("Other player's turn", True, BLACK)
            w, h = n.get_size()
            win.blit(n, ((WIDTH - w) // 2, (MARGIN + BOARD_HEIGHT) * (1 - (color == 'B')) + (MARGIN - h) // 2 + 30))
        else:
            n = SMALL_FONT.render("Your turn.", True, BLACK)
            w, h = n.get_size()
            win.blit(n, ((WIDTH - w) // 2, (MARGIN + BOARD_HEIGHT) * (1 -(self.turn == BLACK)) +(MARGIN - h) // 2 + 30))

    def lift_wall(self):
        """
        Lift a wall. The wall that will be lifted is the first wall in the player's list that hasn't been placed yet.
        This function will only be used for human players because the computer can automatically place a wall without
        having to lift it first

        :return: Whether wall is lifted.
        """
        if self.selected:
            self.select((ROWS,ROWS))  # If a piece was chosen, unselect the piece and select a wall instead.
        turn = self.turn == BLACK
        if self.walls_remaining[turn] == 0:
            return False  # If player 1 has no walls left, they can't lift another wall
        self.wall_selected['sel'] = not self.wall_selected['sel']  # if wall is lifted, unlift. else, lift.
        return True  # function successfully completed

    def update(self, win, pos=None, color=None):
        """
        Every frame, the update function will run. This takes care of the graphics so that they truly remain correct
        throughout each frame

        :param win: Window
        :param pos: Mouse position
        :param color: In the case of an online game, the color of the client.
        """
        self.board.draw(win)  # This will draw the tiles, walls and pawns
        self.draw_moves(win)  # This will draw the possible moves as long as there is a selected piece
        self.walls_left(win, color)  # This updates in the margins that they will have the correct amount written
        if self.wall_selected['sel']:  # If wall is being lifted, constantly make the wall follow the position of mouse
            if pos is not None:
                pygame.draw.line(win, RED, (pos[0]-1, pos[1]-1), (pos[0]-1+WALL_HEIGHT*(1-self.wall_selected['dir']),
                                                                  pos[1]-1+WALL_HEIGHT*(self.wall_selected['dir'])),
                                 WALL_WIDTH+1)
        pygame.display.update()

    def evaluate(self):
        """
        Used for ai

        :return: The value of the current position (how good it is for the white player). White will want to
        maximize this value while black will want to minimize it (minimax). Value composed of distance from
        """
        possible = self.board.possible_moves()
        try:
            return len(self.board.BFS_SP(BLACK, possible))-len(self.board.BFS_SP(WHITE,possible)) + \
                   (self.walls_remaining[0]-self.walls_remaining[1])*0.1
        except TypeError:
            return float('inf')

    def unlift(self):
        """
        Stops lifting wall (sel = false)
        """
        self.wall_selected['sel'] = False

    def make_horizontal(self):
        """
        Makes wall horizontal (dir = 0)
        """
        self.wall_selected['dir'] = 0

    def __repr__(self):
        return f"Game with board {self.board}. {'White' if self.turn==WHITE else 'Black'} turn."

    """def win_possible(self, pos, path, color):
        # Recursive function that checks if it's possible foa piece of color 'color' to win from its current pos 'pos'
        # :param pos: Position on board that is being checked
        # :param path: List of all tiles that were already checked (so that it doesn't keep checking the same tiles)
        # :param color: Color of piece that is being checked (white needs to get to top, black needs to get to bottom)
        if pos in path:
            return False
        path.append(pos)
        if (color == WHITE and pos in TOP_ROW) or (color==BLACK and pos in BOTTOM_ROW):
            return True
        else:
            return any([self.win_possible(p, path, color) for p in self.possible[pos]])
            # Return true if it is r possible to win from any of the tiles that the piece can move to
            def relevant_possible_walls(self):
        #This will be a heavy function because it will check for each wall placement possible if the wall can be placed.
        #This function will be called at the beginning of the turn for the ai, therefore no wall has been lifted yet.
        #:return: List of all possible wall positions. walls = []
        if self.lift_wall():  # Lift outside of board
            for i in range(ROWS):  # Check all vertical walls
                for j in range(ROWS):
                    if self.wall_relevant((i,j), 1, self.turn):
                        walls.append(((i,j), 1))
                    self.flip()
                    if self.wall_relevant((i,j), 0, self.turn):
                        walls.append(((i,j),0))
                    self.flip()
            self.wall_selected['sel'] = False
        return walls
            def wall_relevant(self, pos, dir, turn):
        x,y = pos
        px, py = self.board.pieces[turn == BLACK].pos  # Piece x, piece y
        if self.lift_wall() and self.board.can_place_tech(self.wall_selected, pos):
            if dir: # Vertical
                if x==px and y==py or x-1==px and y==py or x==px and y+1==py or x-1==px and y+1==py:  #Adjacent to piece
                    return self.board.can_place(self.wall_selected, pos)
                if (y>0 and (self.board[x][y]['walls'][1] or self.board[x][y-1]['walls'][0])) or 
                (y+2<ROWS and self.board[x][y+2]['walls'][0]):
                    return self.board.can_place(self.wall_selected, pos)
                try:
                    if self.board[x][y+1]['walls'][1] or self.board[x][y+1]['walls'][3] or 
                    self.board[x-1][y]['walls'][1] or self.board[x-1][y+1]['walls'][1] or 
                    self.board[x-1][y+1]['walls'][3]:
                        return self.board.can_place(self.wall_selected, pos)
                except IndexError:
                    print(f"{x}, {y+1}, {self.board[x][y+1]['walls']}")
                    return False
            else:
                if x==px and y==py or x+1==px and y==py or x==px and y-1==py or x+1==px and y-1==py:
                    return self.board.can_place(self.wall_selected, pos)
                if (x>0 and (self.board[x-1][y]['walls'][1]) or self.board[x][y]['walls'][0]) or 
                (x+2<ROWS and self.board[x+2][y]['walls'][1]):
                    return self.board.can_place(self.wall_selected, pos)
                if self.board[x+1][y]['walls'][0] or self.board[x+1][y]['walls'][2] or self.board[x][y-1]['walls'][0] or
                 self.board[x+1][y-1]['walls'][0] or self.board[x+1][y-1]['walls'][2]:
                    return self.board.can_place(self.wall_selected, pos)
        return False


"""