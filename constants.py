import pygame
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 20
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
GRAY = (40, 40, 40)
DARK_BLUE = (0, 0, 139)
FRIGHTENED_COLOR = (100, 100, 255)
GREEN = (0, 255, 0)

# Game states
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
    ALGORITHM_SELECT = 5

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# Algorithm types
class Algorithm(Enum):
    A_STAR = 0
    BFS = 1
    MINIMAX = 2