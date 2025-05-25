import pygame
import math
from constants import *

class Pacman:
    def __init__(self, position):
        self.position = list(position)
        self.direction = STOP
        self.next_direction = STOP
        self.speed = 2
        self.powered_speed = 2.5  
        self.radius = GRID_SIZE // 2 - 2
        self.score = 0
        self.lives = 3
        self.powered_up = False
        self.power_timer = 0
        self.animation_frame = 0
        self.mouth_angle = 0
        self.mouth_opening = True
        self.initial_position = list(position)
        self.death_animation_frame = 0
        self.is_dying = False
    
    def move(self, maze):
        if self.is_dying:
            return
            
        current_speed = self.powered_speed if self.powered_up else self.speed
        
        next_pos = [
            self.position[0] + self.next_direction[0] * current_speed,
            self.position[1] + self.next_direction[1] * current_speed
        ]
        grid_pos = (int(next_pos[0] // GRID_SIZE), int(next_pos[1] // GRID_SIZE))
        
        if 0 <= grid_pos[0] < COLS and 0 <= grid_pos[1] < ROWS:
            if maze[grid_pos[1]][grid_pos[0]] != 1:
                self.direction = self.next_direction
        
        new_pos = [
            self.position[0] + self.direction[0] * current_speed,
            self.position[1] + self.direction[1] * current_speed
        ]
        grid_pos = (int(new_pos[0] // GRID_SIZE), int(new_pos[1] // GRID_SIZE))
        
        if 0 <= grid_pos[0] < COLS and 0 <= grid_pos[1] < ROWS:
            if maze[grid_pos[1]][grid_pos[0]] != 1:
                self.position = new_pos
        
        if self.position[0] < 0:
            self.position[0] = WIDTH
        elif self.position[0] > WIDTH:
            self.position[0] = 0
        
        self.animation_frame += 1
        if self.animation_frame % 5 == 0:
            if self.mouth_opening:
                self.mouth_angle += 0.1
                if self.mouth_angle >= 0.5:
                    self.mouth_opening = False
            else:
                self.mouth_angle -= 0.1
                if self.mouth_angle <= 0:
                    self.mouth_opening = True
    
    def draw(self, screen):
        if self.is_dying:
            max_frames = 30
            if self.death_animation_frame < max_frames:
                radius = max(0, self.radius - (self.radius * self.death_animation_frame / max_frames))
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.position[0]), int(self.position[1])), 
                                 int(radius))
                self.death_animation_frame += 1
            return
            
        pygame.draw.circle(screen, YELLOW, (int(self.position[0]), int(self.position[1])), self.radius)
        
        if self.direction != STOP:
            if self.direction == RIGHT:
                start_angle = -self.mouth_angle
                end_angle = self.mouth_angle
            elif self.direction == LEFT:
                start_angle = math.pi - self.mouth_angle
                end_angle = math.pi + self.mouth_angle
            elif self.direction == DOWN:
                start_angle = math.pi/2 - self.mouth_angle
                end_angle = math.pi/2 + self.mouth_angle
            elif self.direction == UP:
                start_angle = 3*math.pi/2 - self.mouth_angle
                end_angle = 3*math.pi/2 + self.mouth_angle
            
            points = []
            points.append((int(self.position[0]), int(self.position[1])))
            
            for angle in range(int(start_angle * 180/math.pi), int(end_angle * 180/math.pi) + 1, 5):
                rad = math.radians(angle)
                points.append((
                    int(self.position[0] + math.cos(rad) * self.radius),
                    int(self.position[1] + math.sin(rad) * self.radius)
                ))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, BLACK, points)
    
    def get_grid_position(self):
        return (int(self.position[0] // GRID_SIZE), int(self.position[1] // GRID_SIZE))
    
    def reset(self):
        self.position = list(self.initial_position)
        self.direction = STOP
        self.next_direction = STOP
        self.powered_up = False
        self.power_timer = 0
        self.is_dying = False
        self.death_animation_frame = 0
    
    def start_death_animation(self):
        self.is_dying = True
        self.death_animation_frame = 0