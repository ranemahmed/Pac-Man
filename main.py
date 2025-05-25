import pygame
import sys
import math
from constants import *
from pacman import Pacman
from ghost import Ghost
from maze import create_maze_layout, draw_maze
from game_utils import check_collision, reset_game, draw_text, draw_lives, draw_algorithm_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()
    
    # Game state variables
    game_state = GameState.ALGORITHM_SELECT
    selected_algorithm = None
    algorithm_options = list(Algorithm)
    current_option_index = 0
    
    debug_mode = False
    
    # Initialize game objects (will be reset when game starts)
    pacman = None
    ghosts = []
    maze_layout = []
    level = 1
    max_levels = 3
    dots_eaten = 0
    total_dots = 0
    paused = False
    
    # Ghost activation schedule
    ghost_activation = {
        1: ["blinky"],
        2: ["blinky", "pinky"],
        3: ["blinky", "pinky", "inky", "clyde"]
    }
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == GameState.ALGORITHM_SELECT:
                    if event.key == pygame.K_UP:
                        current_option_index = (current_option_index - 1) % len(algorithm_options)
                        selected_algorithm = algorithm_options[current_option_index]
                    elif event.key == pygame.K_DOWN:
                        current_option_index = (current_option_index + 1) % len(algorithm_options)
                        selected_algorithm = algorithm_options[current_option_index]
                    elif event.key == pygame.K_RETURN:
                        # Initialize game with selected algorithm
                        pacman = Pacman((14 * GRID_SIZE + GRID_SIZE // 2, 23 * GRID_SIZE + GRID_SIZE // 2))
                        
                        ghosts = [
                            Ghost((14 * GRID_SIZE + GRID_SIZE // 2, 11 * GRID_SIZE + GRID_SIZE // 2), RED, "blinky", selected_algorithm),
                            Ghost((14 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2), PINK, "pinky", selected_algorithm),
                            Ghost((12 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2), CYAN, "inky", selected_algorithm),
                            Ghost((16 * GRID_SIZE + GRID_SIZE // 2, 14 * GRID_SIZE + GRID_SIZE // 2), ORANGE, "clyde", selected_algorithm)
                        ]
                        
                        maze_layout = create_maze_layout()
                        total_dots = sum(row.count(2) for row in maze_layout)
                        dots_eaten = 0
                        level = 1
                        
                        for ghost in ghosts:
                            ghost.active = ghost.name in ghost_activation[level]
                        
                        game_state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_d:  # Start debug mode
                        debug_mode = not debug_mode
                
                elif game_state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        game_state = GameState.ALGORITHM_SELECT
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                elif game_state == GameState.PLAYING:
                    if event.key == pygame.K_UP:
                        pacman.next_direction = UP
                    elif event.key == pygame.K_DOWN:
                        pacman.next_direction = DOWN
                    elif event.key == pygame.K_LEFT:
                        pacman.next_direction = LEFT
                    elif event.key == pygame.K_RIGHT:
                        pacman.next_direction = RIGHT
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_d:  # Start debug mode
                        debug_mode = not debug_mode
                    elif event.key == pygame.K_ESCAPE:
                        game_state = GameState.MENU
                
                elif game_state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        # Advance to next level
                        level += 1
                        if level > max_levels:
                            game_state = GameState.GAME_OVER
                        else:
                            # Reset for new level
                            maze_layout = create_maze_layout()
                            total_dots = sum(row.count(2) for row in maze_layout)
                            dots_eaten = 0
                            pacman.reset()
                            for ghost in ghosts:
                                ghost.reset()
                                ghost.active = ghost.name in ghost_activation[level]
                            game_state = GameState.PLAYING
                
                elif game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        # Return to algorithm selection
                        game_state = GameState.ALGORITHM_SELECT
                        debug_mode = False
                    elif event.key == pygame.K_ESCAPE:
                        game_state = GameState.MENU
        
        if game_state == GameState.ALGORITHM_SELECT:
            draw_algorithm_menu(screen, selected_algorithm)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        if game_state == GameState.MENU:
            screen.fill(BLACK)
            draw_text(screen, "PAC-MAN", 72, YELLOW, WIDTH//2, HEIGHT//2 - 100)
            draw_text(screen, "Press ENTER to Start", 36, WHITE, WIDTH//2, HEIGHT//2 + 50)
            draw_text(screen, "Press ESC to Quit", 36, WHITE, WIDTH//2, HEIGHT//2 + 100)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        if paused:
            screen.fill(BLACK)
            draw_text(screen, "PAUSED", 72, YELLOW, WIDTH//2, HEIGHT//2 - 50)
            draw_text(screen, "Press P to continue", 36, WHITE, WIDTH//2, HEIGHT//2 + 50)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        if game_state == GameState.LEVEL_COMPLETE:
            screen.fill(BLACK)
            draw_text(screen, f"LEVEL {level} COMPLETE!", 72, YELLOW, WIDTH//2, HEIGHT//2 - 50)
            draw_text(screen, f"Score: {pacman.score}", 36, WHITE, WIDTH//2, HEIGHT//2 + 20)
            if level < max_levels:
                draw_text(screen, "Press ENTER for Next Level", 36, WHITE, WIDTH//2, HEIGHT//2 + 70)
            else:
                draw_text(screen, "You beat all levels!", 36, WHITE, WIDTH//2, HEIGHT//2 + 70)
                draw_text(screen, "Press ENTER to continue", 36, WHITE, WIDTH//2, HEIGHT//2 + 120)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        if game_state == GameState.GAME_OVER:
            screen.fill(BLACK)
            draw_text(screen, "GAME OVER", 72, RED, WIDTH//2, HEIGHT//2 - 50)
            draw_text(screen, f"Final Score: {pacman.score}", 36, WHITE, WIDTH//2, HEIGHT//2 + 20)
            draw_text(screen, "Press R to Restart", 36, WHITE, WIDTH//2, HEIGHT//2 + 70)
            draw_text(screen, "Press ESC for Menu", 36, WHITE, WIDTH//2, HEIGHT//2 + 120)
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # Game logic
        if pacman.is_dying:
            if pacman.death_animation_frame >= 30:
                if pacman.lives <= 0:
                    game_state = GameState.GAME_OVER
                else:
                    pacman.reset()
                    for ghost in ghosts:
                        ghost.reset()
                        ghost.active = ghost.name in ghost_activation[level]
            else:
                screen.fill(BLACK)
                draw_maze(screen, maze_layout)
                pacman.draw(screen)
                for ghost in ghosts:
                    ghost.draw(screen)
                pygame.display.flip()
                clock.tick(60)
                continue
                
        pacman.move(maze_layout)
        
        # Check dot/power pellet collection
        grid_x, grid_y = pacman.get_grid_position()
        if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
            if maze_layout[grid_y][grid_x] == 2:
                maze_layout[grid_y][grid_x] = 0
                pacman.score += 10
                dots_eaten += 1
            elif maze_layout[grid_y][grid_x] == 3:
                maze_layout[grid_y][grid_x] = 0
                pacman.score += 50
                pacman.powered_up = True
                pacman.power_timer = 10 * 40
                for ghost in ghosts:
                    if ghost.active:
                        ghost.set_frightened(pacman.power_timer)
        
        # Update power pellet timer
        if pacman.powered_up:
            pacman.power_timer -= 1
            if pacman.power_timer <= 0:
                pacman.powered_up = False
        
        # Move ghosts
        for ghost in ghosts:
            if ghost.active:
                ghost.move(maze_layout, pacman, ghosts)
        
        # Check collisions
        collision_result = check_collision(pacman, ghosts)
        if collision_result > 0:
            pacman.score += collision_result
        elif collision_result == -1:
            pass  
        
        # Level completion check
        if dots_eaten >= total_dots:
            game_state = GameState.LEVEL_COMPLETE
        
        # Drawing
        screen.fill(BLACK)
        draw_maze(screen, maze_layout)
        
        # Draw debug information if enabled
        if debug_mode:
            for ghost in ghosts:
                if ghost.active and hasattr(ghost, 'draw_debug'):
                    ghost.draw_debug(screen)
        
        pacman.draw(screen)
        for ghost in ghosts:
            if ghost.active:
                ghost.draw(screen)
        
        ui_y = HEIGHT - 25
        draw_text(screen, f"SCORE: {pacman.score}", 24, WHITE, 100, ui_y, "left")
        draw_text(screen, f"LEVEL: {level}", 24, WHITE, WIDTH//2, ui_y)
        if selected_algorithm:
            draw_text(screen, f"ALGO: {selected_algorithm.name}", 24, WHITE, WIDTH - 100, ui_y, "right")
        
        lives_x = WIDTH - 180
        for i in range(pacman.lives):
            pygame.draw.circle(screen, YELLOW, (lives_x + i * 25, ui_y), 8)
            pygame.draw.arc(
                screen, BLACK,
                (lives_x + i * 25 - 8, ui_y - 8, 16, 16),
                math.pi/4, math.pi*7/4, 2
            )
        
        if pacman.powered_up:
            timer_width = 100 * (pacman.power_timer / (10 * 60))
            pygame.draw.rect(screen, FRIGHTENED_COLOR, (WIDTH//2 - 50, HEIGHT - 15, timer_width, 10))
        
        if debug_mode:
            draw_text(screen, "DEBUG MODE", 20, GREEN, 10, 10, "left")
            if selected_algorithm:
                draw_text(screen, f"ALGORITHM: {selected_algorithm.name}", 20, GREEN, 10, 30, "left")
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()