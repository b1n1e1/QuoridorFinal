import pygame.gfxdraw
from .pieces import *
from collections import defaultdict, deque


class Board:
    def __init__(self):
        self.board = []
        self.create_board()
        self.pieces = (Pawn(WHITE, WHITE_START), Pawn(BLACK, BLACK_START))

    def create_board(self):
        """
        Creates Board as 2d list. Creates ROWS*ROWS board of tiles, adds white piece on bottom and black piece on top
        """
        self.board = [[{'occupied':False, 'pos':(j*TILE_WIDTH, MARGIN+i*TILE_HEIGHT),
                        'walls':[False for _ in range(4)]} for i in range(ROWS)] for j in range(ROWS)]
        self.board[WHITE_START[0]][WHITE_START[1]]['occupied'] = True
        self.board[BLACK_START[0]][BLACK_START[1]]['occupied'] = True

    def __getitem__(self, item):
        return self.board[item]

    def clone(self):
        a = Board()
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                a.board[i][j]['occupied'] = self.board[i][j]['occupied']
                a.board[i][j]['pos'] = self.board[i][j]['pos']
                walls = self.board[i][j]['walls']
                a.board[i][j]['walls'] = [*walls]
        a.pieces = (self.pieces[0].clone(), self.pieces[1].clone())
        return a

    def get_piece(self, pos):
        """:param pos: Row,col of tile
        :return: The piece that is in the tile. (0 if no piece is in tile)"""
        if self.pieces[0].pos == pos:
            return self.pieces[0]
        elif self.pieces[1].pos == pos:
            return self.pieces[1]
        return 0

    def draw(self, win):
        """
        Draws board (and margins)

        :param win: Screen (window)
        """
        pygame.draw.rect(win, TAN, pygame.Rect(0, 0, WIDTH, MARGIN))  # Top margin
        pygame.draw.rect(win, BROWN, pygame.Rect(0, MARGIN, WIDTH, BOARD_HEIGHT))  # Board background
        pygame.draw.rect(win, TAN, pygame.Rect(0, MARGIN + BOARD_HEIGHT, WIDTH, MARGIN))  # Bottom margin
        for i in range(ROWS):
            for j in range(ROWS):  # For every single tile on board
                rect = pygame.Rect(self.board[i][j]['pos'], (TILE_WIDTH, TILE_HEIGHT))  # Pygame rectangle of tile
                pygame.draw.rect(win, TAN, rect, 4)
                if self.board[i][j]['walls'][0]:  # If the item isn't False
                    pygame.draw.line(win, RED, (i * TILE_WIDTH, j * TILE_HEIGHT + MARGIN - 1),
                                     (i * TILE_WIDTH, (j + 1) * TILE_HEIGHT+MARGIN), WALL_WIDTH + 1)
                if self.board[i][j]['walls'][1]:
                    pygame.draw.line(win, RED, (i * TILE_WIDTH - 1, j * TILE_HEIGHT + MARGIN),
                                     ((i + 1) * TILE_WIDTH, j * TILE_HEIGHT + MARGIN), WALL_WIDTH + 1)
        for pawn in self.pieces:
            pawn.draw(win)

    def move(self, piece, pos):
        """
        Move piece from one position to another

        :param piece: Moving piece
        :param pos: New position
        """
        self.board[piece.pos[0]][piece.pos[1]]['occupied'] = False  # The tile the piece was in is no longer occupied
        self.board[pos[0]][pos[1]]['occupied'] = True  # The tile the piece is moving to is now occupied.
        piece.move(pos)

    def place_wall(self, wall):
        """
        Place wall in pos

        :param wall: Tuple (pos, dir)
        """
        x,y = wall[0]  # x:row, y:col
        if wall[1] == 1:  # If wall is vertical
            self.board[x][y]['walls'][0] = True
            self.board[x-1][y]['walls'][2] = True
            self.board[x][y+1]['walls'][0] = True
            self.board[x-1][y+1]['walls'][2] = True
        else:  # If wall is horizontal
            self.board[x][y]['walls'][1] = True
            self.board[x][y-1]['walls'][3] = True
            self.board[x+1][y]['walls'][1] = True
            self.board[x+1][y-1]['walls'][3] = True

    def unplace_wall(self, wall):
        """
        Remove wall from board.

        :param wall: Tuple of (pos, dir)
        """
        x,y = wall[0]  # row,col of top/left point of wall
        if wall[1] == 1:
            self.board[x][y]['walls'][0] = 0
            self.board[x-1][y]['walls'][2] = 0
            self.board[x][y+1]['walls'][0] = 0
            self.board[x-1][y+1]['walls'][2] = 0
        else:  # If wall is horizontal
            self.board[x][y]['walls'][1] = 0
            self.board[x][y-1]['walls'][3] = 0
            self.board[x+1][y]['walls'][1] = 0
            self.board[x+1][y-1]['walls'][3] = 0

    def can_place_tech(self, wall):
        """
        Checks if given wall can be placed in given pos technically (not crossing other walls or the side of board)

        :param wall: Tuple -> pos, direction
        :return: True if wall can be placed, False if not (Doesn't place wall either case)
        """
        x, y = wall[0]
        if y > ROWS-1 or y < 0:
            return False
        if wall[1] == 1:
            if x == 0 or x == ROWS or y >= ROWS-1 or y < 0:
                return False
            if self.board[x][y]['walls'][0] or self.board[x][y+1]['walls'][0]:  # If theres a wall in same col and pos
                return False
            if self.board[x-1][y+1]['walls'][1] and self.board[x][y+1]['walls'][1]:  # If wall is crossing another wall
                return False
        else:
            if x >= ROWS-1 or x < 0 or y == 0 or y == ROWS:
                return False
            if self.board[x][y]['walls'][1] or self.board[x+1][y]['walls'][1]:  # If theres a wall in same row and pos
                return False
            if self.board[x+1][y-1]['walls'][0] and self.board[x+1][y]['walls'][0]:  # If wall is crossing another wall
                return False
        return True

    def can_place(self, wall):
        """
        Checks if a wall can be placed at pos

        :param wall: Tuple -> (pos, dir) -> ((int,int), int)
        :return: Whether wall can be placed or not
        """
        x = False
        if self.can_place_tech(wall):  # If walls aren't intercepting, crossing each other
            self.place_wall(wall)  # Place wall (only for sake of seeing if move is illegal
            possible = self.possible_moves()  # Only needed for DFS function. Dict of all moves
            x = self.DFS(WHITE, possible) and self.DFS(BLACK, possible)  # True if there is a path to end
            self.unplace_wall(wall)  # Unplace wall (this function is only supposed to check if the wall can be placed)
        return x  # If move is legal, return true else false

    def possible_moves(self):
        moves = defaultdict(set)
        for x in range(ROWS):
            for y in range(ROWS):
                walls = self.board[x][y]['walls']
                if y > 0 and not walls[1]:  # Moving up -> No wall above and not on top row
                    if self.board[x][y-1]['occupied']:  # If the tile above is occupied
                        if y-1>0 and not self.board[x][y-1]['walls'][1]:  # If no wall (or border) over piece above
                            moves[(x,y)].add((x, y-2))
                        else:  # If there's a wall over the piece above
                            if not self.board[x][y-1]['walls'][0] and x>0:  # If there's no wall left of piece above
                                moves[(x,y)].add((x-1,y-1))
                            if not self.board[x][y-1]['walls'][2] and x<ROWS-1:  # If no wall right of piece above
                                moves[(x,y)].add((x+1,y-1))
                    else:  # If the tile above is empty
                        moves[(x,y)].add((x, y-1))
                if x > 0 and not walls[0]:  # Moving left -> No wall on the left and not on first column
                    if self.board[x-1][y]['occupied']:  # If the tile to the left is occupied
                        if x-1>0 and not self.board[x-1][y]['walls'][0]:  # If there's no wall behind piece to the left
                            moves[(x,y)].add((x-2, y))
                        else:  # If there is a wall (or border) behind the piece to the left
                            if not self.board[x-1][y]['walls'][1] and y>0:  # If there's no wall above piece to the left
                                moves[(x,y)].add((x-1,y-1))
                            if not self.board[x-1][y]['walls'][3] and y<ROWS-1:  # If no wall below piece to the left
                                moves[(x,y)].add((x-1,y+1))
                    else:  # If the tile to the left is empty
                        moves[(x,y)].add((x-1, y))
                if x < ROWS - 1 and not walls[2]:  # Moving right -> No wall on the right and not on last column
                    if self.board[x+1][y]['occupied']:  # If the tile to the right is occupied
                        if x+1<ROWS-1 and not self.board[x+1][y]['walls'][2]:  # If no wall behind piece to right
                            moves[(x,y)].add((x+2, y))
                        else:  # If there is a wall (or border) behind piece to right
                            if not self.board[x+1][y]['walls'][1] and y>0:  # If there's no wall above piece to right
                                moves[(x,y)].add((x+1,y-1))
                            if not self.board[x+1][y]['walls'][3] and y<ROWS-1:  # If no wall below piece to right
                                moves[(x,y)].add((x+1,y+1))
                    else:  # If the tile to the right is empty
                        moves[(x,y)].add((x+1, y))

                if y < ROWS - 1 and not walls[3]:  # Moving down -> No wall beneath and not on bottom row
                    if self.board[x][y+1]['occupied']:  # If the tile below is occupied
                        if y+1<ROWS-1 and not self.board[x][y+1]['walls'][3]:  # If there's no wall under piece below
                            moves[(x,y)].add((x, y+2))
                        else:  # If there's a wall under the piece below
                            if not self.board[x][y+1]['walls'][0] and x>0:  # If there's no wall left of piece below
                                moves[(x,y)].add((x-1,y+1))
                            if not self.board[x][y+1]['walls'][2] and x<ROWS-1:  # If no wall right of piece below
                                moves[(x,y)].add((x+1,y+1))
                    else:  # If the tile below is empty
                        moves[(x,y)].add((x, y+1))
        return moves

    def BFS_SP(self, color, moves):
        """
        Breadth First Search: Shortest path from start to goal.

        :param color: Color of piece
        :param moves: Graph (default dict) of possible moves
        :return: Shortest path or infinity if no path
        """
        start = self.pieces[color==BLACK].pos  # start is the position of the pawn of color Color
        goal = TOP_ROW if color==WHITE else BOTTOM_ROW
        seen = set()  # set of all edges (keys) already checked
        queue = deque()
        queue.append([start])  # queue is a queue of lists of the shortest paths
        if start in goal:
            return [start]
        while queue:
            path = queue.popleft()  # one path is removed from the head of the queue
            node = path[-1]  # node = last edge in path
            if node not in seen:  # if node hasn't been explored yet, if it was explored, this couldn't be shortest path
                neighbors = moves[node]  # neighbors -> list of all edges that node can reach
                for neighbor in neighbors:
                    new_path = [*path, neighbor]  # queue will append a new path for each of the neighbors of node
                    queue.append(new_path)
                    if neighbor in goal:
                        return new_path  # if the end has been reached, this is the shortest path
                seen.add(node)  # check given node as seen
        return float("Inf")  # If the queue was completely checked and emptied, there's no path

    def DFS(self, color, moves):
        """
        Depth first search - Find if there is a path from piece of color color to the goal

        :param color: Color of piece being checked
        :param moves: Graph of moves
        :return: True if there is a path, False if there isn't
        """
        start = self.pieces[color == BLACK].pos  # start is the position of the piece of color 'color'
        goal = TOP_ROW if color == WHITE else BOTTOM_ROW  # if piece is black, they need to get to bottom, vice versa
        seen, stack = set(), [start]  # seen is set of visited positions, stack is the stack used to check
        while stack:  # while the stack isn't empty
            node = stack.pop()  # node is the last element of the stack, a pos on the board
            seen.add(node)  # add current node to all nodes that have been checked
            for neighbor in moves[node]:  # for every move that can be done at pos node
                if neighbor in goal:  # if neighbor is in the goal row
                    return True
                if neighbor not in seen:  # if neighbor hasn't been checked yet
                    stack.append(neighbor)  # add neighbor to the stack to be checked
        return False  # the stack is empty and all possibilities were checked.

    def winner(self):
        """
        :return: WHITE if any of the tiles on top are occupied by white, BLACK if any of the tiles on bottom are
        occupied by black, None if neither.
        """
        if self.pieces[0].pos[1] == 0:  # if white piece is in top row
            return WHITE
        if self.pieces[1].pos[1] == ROWS-1:  # if black piece is in bottom row
            return BLACK
