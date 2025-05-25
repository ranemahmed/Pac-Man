import pygame
import math
from constants import *

def check_collision(pacman, ghosts):
    if pacman.is_dying:
        return 0
        
    pacman_rect = pygame.Rect(
        pacman.position[0] - pacman.radius,
        pacman.position[1] - pacman.radius,
        pacman.radius * 2,
        pacman.radius * 2
    )
    
    for ghost in ghosts:
        if not ghost.active:
            continue
            
        ghost_rect = pygame.Rect(
            ghost.position[0] - ghost.radius,
            ghost.position[1] - ghost.radius,
            ghost.radius * 2,
            ghost.radius * 2
        )
        
        if pacman_rect.colliderect(ghost_rect):
            if pacman.powered_up and ghost.mode != "eaten":
                ghost.mode = "eaten"
                ghost.speed = ghost.eaten_speed
                ghost.in_house = False 
                return 200
            elif ghost.mode != "eaten" and ghost.mode != "frightened":
                pacman.lives -= 1
                pacman.start_death_animation()
                return -1
    
    return 0

def reset_game(pacman, ghosts, maze):
    pacman.reset()
    
    for ghost in ghosts:
        ghost.reset()
    
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 0:
                maze[y][x] = 2
            if (x, y) in [(1, 3), (28, 3), (1, 23), (28, 23)]:
                maze[y][x] = 3

def draw_text(screen, text, size, color, x, y, align="center"):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.topleft = (x, y)
    elif align == "right":
        text_rect.topright = (x, y)
    
    screen.blit(text_surface, text_rect)

def draw_lives(screen, lives, x, y):
    for i in range(lives):
        pygame.draw.circle(
            screen, YELLOW,
            (x + i * 25, y),
            GRID_SIZE // 2 - 2
        )
        pygame.draw.arc(
            screen, BLACK,
            (x + i * 25 - (GRID_SIZE // 2 - 2), y - (GRID_SIZE // 2 - 2),
             (GRID_SIZE - 4), (GRID_SIZE - 4)),
            math.pi/4, math.pi*7/4, 2
        )

def draw_algorithm_menu(screen, selected_algorithm):
    screen.fill(BLACK)
    draw_text(screen, "SELECT GHOST ALGORITHM", 48, YELLOW, WIDTH//2, HEIGHT//2 - 100)
    
    algorithms = [
        ("A* Search", Algorithm.A_STAR),
        ("Breadth-First Search", Algorithm.BFS),
        ("Minimax", Algorithm.MINIMAX)
    ]
    
    for i, (text, algo) in enumerate(algorithms):
        color = GREEN if selected_algorithm == algo else WHITE
        draw_text(screen, text, 36, color, WIDTH//2, HEIGHT//2 + i * 40)
    
    draw_text(screen, "Press ENTER to Confirm", 24, WHITE, WIDTH//2, HEIGHT//2 + 200)
    draw_text(screen, "Use UP/DOWN arrows to select", 24, WHITE, WIDTH//2, HEIGHT//2 + 240)