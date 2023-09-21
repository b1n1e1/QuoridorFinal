from quoridor.constants import *
import random


class AI:

    ALL_WALLS_HORIZONTAL = *((i,j) for i in range(ROWS-1) for j in range(1,ROWS)),  # tuple of all horizontal placements
    ALL_WALLS_VERTICAL = *((i,j) for i in range(1,ROWS) for j in range(ROWS-1)),  # tuple of all vertical placements

    def __init__(self, typ=0):
        if typ not in range(7):  # if the user enters a number other than the range 0-6
            raise ValueError
        self.type = typ
        if typ == 1:
            print('You have selected Minimax, the best performing AI. Take in mind it may take several seconds to make'
                  'a decision')

    def do(self, game):
        ais = [0, self.pick_move, self.greediest_ai, self.random_ai, self.hesitant_ai, self.greedy_ai, self.passive_ai]
        if self.type != 0:
            game = ais[self.type](game)
        else:
            self.type = random.randint(2,6)
            self.do(game)
            self.type = 0
        return game

    @staticmethod
    def place_wall_above(game):
        """
        Places wall over the white player

        :param game: Game
        :return: True if wall was placed, False otherwise
        """
        white_piece = game.board.pieces[0].pos
        if game.lift_wall():
            game.make_horizontal()
            if game.place(white_piece):  # try placing right over piece
                return True
            game.lift_wall()
            if game.place((white_piece[0] - 1, white_piece[1])):  # try placing to the left over piece
                return True
            game.unlift()
        return False

    @staticmethod
    def go_shortest_path(game):
        """
        Makes AI take the shortest path based on the BFS

        :param game: Game
        """
        piece = game.board.pieces[1].pos  # position of black piece
        game.select((piece[0] * TILE_WIDTH, piece[1] * TILE_HEIGHT + MARGIN))  # select black piece
        possible_moves = game.board.possible_moves()
        best_path = game.board.BFS_SP(BLACK, possible_moves)
        chosen = best_path[1]
        game.select((chosen[0] * TILE_WIDTH, chosen[1] * TILE_HEIGHT + MARGIN))

    @staticmethod
    def minimax(game, depth, maximizing_player):
        """
        Minimax Algorithm

        :param game: Game that is being checked
        :param depth: How many recursions have been done
        :param maximizing_player: True if white, False if white
        :return: Best minimax value, game after the best minimax value has been done
        """
        x = game.winner()
        if x is not None:
            return float('inf') if x == WHITE else float('-inf'), game
        if depth == 2:  # If depth has reached 2 or if the game is over
            return game.evaluate(), game
        best = float('-inf') if maximizing_player else float('inf')  # min value if maximizing, max if minimizing
        best_move = None
        piece = game.board.pieces[game.turn == BLACK].pos  # position of piece that is moving
        game.select((piece[0] * TILE_WIDTH, piece[1] * TILE_HEIGHT + MARGIN))  # select piece to get valid moves
        for move in game.valid_moves:  # For every move in the valid moves
            new_game = game.clone()  # Create copy of game
            piece = new_game.board.pieces[new_game.turn == BLACK].pos  # position of piece that is moving
            new_game.select((piece[0] * TILE_WIDTH, piece[1] * TILE_HEIGHT + MARGIN))
            new_game.move(move)  # move piece to current valid move
            # noinspection PyUnresolvedReferences
            value = AI.minimax(new_game, depth + 1, not maximizing_player)[0]  # recursion, does minimax
            if maximizing_player:  # minimax
                best = max(best, value)
            else:
                best = min(best, value)
            if best == value:
                best_move = new_game  # if the current value is the best value, the best move is the move that was done
        if game.walls_remaining[not maximizing_player]:  # if there are any walls left for the current player
            for wall in AI.ALL_WALLS_HORIZONTAL:  # for each possible wall
                if game.board.can_place((wall, 0)):
                    new_game = game.clone()
                    new_game.place_ai(wall, 0)
                    value = AI.minimax(new_game, depth + 1, not maximizing_player)[0]
                else:
                    continue
                if maximizing_player:
                    best = max(best, value)
                else:
                    best = min(best, value)
                if best == value:
                    best_move = new_game
            if game.turns > 10:
                for wall in AI.ALL_WALLS_VERTICAL:
                    new_game = game.clone()
                    if new_game.board.can_place((wall, 1)):
                        new_game.place_ai(wall, 1)
                        value = AI.minimax(new_game, depth + 1, not maximizing_player)[0]
                    else:
                        continue
                    if maximizing_player:
                        best = max(best, value)
                    else:
                        best = min(best, value)
                    if best == value:
                        best_move = new_game
        return best, best_move

    @staticmethod
    def greediest_ai(game):
        if AI.place_wall_above(game):
            return game
        AI.go_shortest_path(game)
        return game

    @staticmethod
    def random_ai(game):
        x = random.randint(0,1)
        if x == 1:
            if AI.place_wall_above(game):
                return game
        AI.go_shortest_path(game)
        return game

    @staticmethod
    def hesitant_ai(game):
        x = random.randint(1,4)
        if x == 4:
            if AI.place_wall_above(game):
                return game
        AI.go_shortest_path(game)
        return game

    @staticmethod
    def greedy_ai(game):
        x = random.randint(1,3)
        if x != 3:
            if AI.place_wall_above(game):
                return game
        AI.go_shortest_path(game)
        return game

    @staticmethod
    def passive_ai(game):
        AI.go_shortest_path(game)
        return game

    @staticmethod
    @timeit
    def pick_move(game):
        return AI.minimax(game, 0, False)[1]
