import pygame.font
from datetime import datetime
pygame.font.init()

# Sizes
WIDTH, HEIGHT = 450, 670
ROWS = 9  # Amount of rows and columns, board needs to be square so rows=columns
MARGIN = 110  # Size of margin
BOARD_HEIGHT = HEIGHT - (2 * MARGIN)  # The height of the board is the height of the window - the heights of the margins

TILE_WIDTH = WIDTH//ROWS  # The width of the tiles is the width of the window // amount of columns
TILE_HEIGHT = BOARD_HEIGHT//ROWS  # The height of the tiles is the height of the board // amount of rows (==TILE_WIDTH)

WALLS = 10
WALL_WIDTH = 5
WALL_HEIGHT = 2 * TILE_HEIGHT  # Each wall is the height of 2 tiles
PAWN_RADIUS = TILE_WIDTH//3  # The diameter of a pawn is 2/3 the width of a tile
MOVE_RADIUS = TILE_WIDTH//7  # The diameter of a possible move is 2/7 the width of a tile

# Positions
WHITE_START = ((ROWS-1)//2, ROWS-1)
BLACK_START = ((ROWS-1)//2, 0)
BOTTOM_ROW = {(i,ROWS-1) for i in range(ROWS)}  # All positions in bottom row
TOP_ROW = {(i,0) for i in range(ROWS)}  # All positions in top row

# Font
FONT = pygame.font.SysFont('Comic Sans ms', 30)
SMALL_FONT = pygame.font.SysFont('Comic Sans ms', 20)

# Colors - RGB form tuples
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TAN = (210, 180, 140)
BROWN = (64, 32, 11)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
LIGHT_BLUE = (52, 155, 229)
LIGHT_PINK = (214, 105, 255)


def timeit(func):
    def inner(*args, **kwargs):
        tim = datetime.now()
        x = func(*args, **kwargs)
        print(f'{func.__name__} executed in {datetime.now()-tim}')
        return x
    return inner
