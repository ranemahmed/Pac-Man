import pygame
import math
import random
import heapq
from collections import deque
from node import Node
from constants import *

class Ghost:
    def __init__(self, position, color, name, algorithm=None):
        self.position = list(position)
        self.color = color
        self.name = name
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.speed = 2
        self.initial_speed = 2
        self.radius = GRID_SIZE // 2 - 2
        self.target = None
        self.scatter_target = None
        self.mode = "scatter"
        self.mode_timer = 0
        self.frightened_timer = 0
        self.initial_position = list(position)
        self.animation_frame = 0
        self.eye_direction = STOP
        self.exit_position = (14, 11)
        self.in_house = True
        self.frightened_speed = 0.5
        self.eaten_speed = 3
        self.active = True
        self.algorithm = algorithm
        
        self.scatter_duration = 7
        self.chase_duration = 20
        self.frightened_duration = 10
        
        if name == "blinky":
            self.scatter_target = (COLS - 2, 1)
        elif name == "pinky":
            self.scatter_target = (1, 1)
        elif name == "inky":
            self.scatter_target = (COLS - 2, ROWS - 2)
        elif name == "clyde":
            self.scatter_target = (1, ROWS - 2)
    
    def update_mode(self):
        if self.mode == "frightened":
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = "chase"
                self.mode_timer = self.chase_duration * 60
                self.speed = self.initial_speed
        elif self.mode in ["scatter", "chase"]:
            self.mode_timer -= 1
            if self.mode_timer <= 0:
                if self.mode == "scatter":
                    self.mode = "chase"
                    self.mode_timer = self.chase_duration * 60
                else:
                    self.mode = "scatter"
                    self.mode_timer = self.scatter_duration * 60
    
    def move(self, maze, pacman, other_ghosts=None):
        if not self.active:
            return
            
        self.update_mode()
        
        if self.mode == "eaten" and self.get_grid_position() == self.exit_position:
            self.mode = "chase"
            self.mode_timer = self.chase_duration * 60
            self.in_house = False
            self.speed = self.initial_speed
        
        if self.in_house:
            if self.get_grid_position() != self.exit_position:
                path = self.find_path(maze, self.get_grid_position(), self.exit_position)
                if len(path) > 1:
                    next_pos = path[1]
                    self.direction = (next_pos[0] - self.get_grid_position()[0], 
                                    next_pos[1] - self.get_grid_position()[1])
            else:
                self.in_house = False
                self.mode = "scatter"
                self.mode_timer = self.scatter_duration * 60
        
        grid_pos = self.get_grid_position()
        pixel_pos = (self.position[0] % GRID_SIZE, self.position[1] % GRID_SIZE)
        
        if (pixel_pos[0] < 2 or pixel_pos[0] > GRID_SIZE-2 or 
            pixel_pos[1] < 2 or pixel_pos[1] > GRID_SIZE-2):
            
            if self.mode == "frightened":
                self.move_random(maze)
            elif self.mode == "eaten":
                self.target = self.exit_position
                path = self.find_path(maze, grid_pos, self.target)
                if len(path) > 1:
                    next_pos = path[1]
                    self.direction = (next_pos[0] - grid_pos[0], next_pos[1] - grid_pos[1])
                else: self.move_random(maze)
            else:
                if self.mode == "scatter":
                    self.target = self.scatter_target
                elif self.mode == "chase":
                    self.target = self.get_chase_target(pacman, other_ghosts)
                
                if self.target:
                    path = self.find_path(maze, grid_pos, self.target)
                    if len(path) > 1:
                        next_pos = path[1]
                        self.direction = (next_pos[0] - grid_pos[0], next_pos[1] - grid_pos[1])
        
        new_pos = [
            self.position[0] + self.direction[0] * self.speed,
            self.position[1] + self.direction[1] * self.speed
        ]
        grid_pos = (int(new_pos[0] // GRID_SIZE), int(new_pos[1] // GRID_SIZE))
        
        if 0 <= grid_pos[0] < COLS and 0 <= grid_pos[1] < ROWS:
            if maze[grid_pos[1]][grid_pos[0]] != 1:
                self.position = new_pos
        
        if self.position[0] < 0:
            self.position[0] = WIDTH
        elif self.position[0] > WIDTH:
            self.position[0] = 0
        
        self.eye_direction = self.direction
    
    def find_path(self, maze, start, end):
        if self.algorithm == Algorithm.A_STAR:
            return self.a_star_search(maze, start, end)
        elif self.algorithm == Algorithm.BFS:
            return self.bfs_search(maze, start, end)
        elif self.algorithm == Algorithm.MINIMAX:
            return self.minimax_search(maze, start,pacman_pos=end)
        else:
            return []
    
    def a_star_search(self, maze, start, end):
        start_node = Node(start)
        end_node = Node(end)
        
        open_list = []
        closed_list = set()

        self.debug_open_set = []
        self.debug_closed_set = set()
        
        heapq.heappush(open_list, (start_node.f, start_node))
        self.debug_open_set = []  # For visualization
        self.debug_closed_set = set()  # For visualization

        while open_list:
            current_node = heapq.heappop(open_list)[1]
            closed_list.add(current_node)
            self.debug_closed_set.add(current_node.position)  # Track visted nodes
            
            if current_node == end_node:
                path = []
                while current_node is not None:
                    path.append(current_node.position)
                    current_node = current_node.parent
                    self.debug_path = path[::-1]
                return path[::-1]
            
            for direction in [UP, DOWN, LEFT, RIGHT]:
                node_position = (
                    current_node.position[0] + direction[0],
                    current_node.position[1] + direction[1]
                )
                
                if (node_position[0] < 0 or node_position[0] >= COLS or
                    node_position[1] < 0 or node_position[1] >= ROWS):
                    continue
                
                if maze[node_position[1]][node_position[0]] == 1:
                    continue
                
                new_node = Node(node_position, current_node)
                
                if new_node in closed_list:
                    continue
                
                new_node.g = current_node.g + 1
                new_node.h = abs(new_node.position[0] - end_node.position[0]) + abs(new_node.position[1] - end_node.position[1])
                new_node.f = new_node.g + new_node.h

                self.debug_open_set.append(new_node.position)
                
                for idx, (f, node) in enumerate(open_list):
                    if node == new_node and node.f < new_node.f:
                        break
                else:
                    heapq.heappush(open_list, (new_node.f, new_node))
        
        return []
    
    def bfs_search(self, maze, start, end):
     start_node = Node(start)
     end_node = Node(end)

    # Initialize debug sets
     self.debug_open_set = []  # Nodes in the queue
     self.debug_closed_set = set()  # Visited 
     self.debug_path = [] 
     
     queue = deque()
     queue.append(start_node)
     visited = set()
     visited.add(start_node)
     parent_map = {start_node: None}
    
    # Track initial open set
     self.debug_open_set.append(start_node.position)
    
     while queue:
        current_node = queue.popleft()
        self.debug_closed_set.add(current_node.position)  # Track visited
        
        if current_node == end_node:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = parent_map[current_node]
            self.debug_path = path[::-1]  # Store path for debug
            return path[::-1]
        
        for direction in [UP, DOWN, LEFT, RIGHT]:
            node_position = (
                current_node.position[0] + direction[0],
                current_node.position[1] + direction[1]
            )
            
            if (node_position[0] < 0 or node_position[0] >= COLS or
                node_position[1] < 0 or node_position[1] >= ROWS):
                continue
            
            if maze[node_position[1]][node_position[0]] == 1:
                continue
            
            new_node = Node(node_position)
            
            if new_node not in visited:
                visited.add(new_node)
                parent_map[new_node] = current_node
                queue.append(new_node)
                self.debug_open_set.append(new_node.position)  # Track queue
    
     return []
    
    def minimax_search(self, maze, ghost_pos, pacman_pos, depth=5):
    # Initialize debug sets
     self.debug_open_set = []  # Nodes being evaluated
     self.debug_closed_set = set()  # Evaluated nodes
     self.debug_path = []  
    
     if not (0 <= ghost_pos[0] < len(maze[0])) or not (0 <= ghost_pos[1] < len(maze)):
        self.debug_path = [ghost_pos, ghost_pos]
        return self.debug_path
        
     if not (0 <= pacman_pos[0] < len(maze[0])) or not (0 <= pacman_pos[1] < len(maze)):
        self.debug_path = [ghost_pos, ghost_pos]
        return self.debug_path
    
     def minimax(ghost_pos, pacman_pos, depth, maximizing, alpha, beta):
        current_pos = ghost_pos if maximizing else pacman_pos
        self.debug_closed_set.add(current_pos)  # Track evaluated nodes
        
        if depth == 0 or ghost_pos == pacman_pos:
            return -self.distance(ghost_pos, pacman_pos)

        neighbors = self.get_neighbors(ghost_pos if maximizing else pacman_pos, maze)
        if not neighbors:
            return -self.distance(ghost_pos, pacman_pos)
        
        if maximizing:
            max_eval = -math.inf
            for move in neighbors:
                self.debug_open_set.append(move)  # Track nodes being evaluated
                eval = minimax(move, pacman_pos, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:  # beta cutoff
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in neighbors:
                self.debug_open_set.append(move)  # Track nodes being evaluated
                eval = minimax(ghost_pos, move, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:  # alpha cutoff
                    break
            return min_eval
 
     best_score = -math.inf
     move_choice = ghost_pos
     neighbors = self.get_neighbors(ghost_pos, maze)
     if not neighbors:
        self.debug_path = [ghost_pos, ghost_pos]
        return self.debug_path
    
     alpha = -math.inf
     beta = math.inf
    
     for move in neighbors:
        self.debug_open_set.append(move)  # Track nodes being evaluated
        score = minimax(move, pacman_pos, depth - 1, False, alpha, beta)
        if score > best_score:
            best_score = score
            move_choice = move
        alpha = max(alpha, best_score)

    
    # Convert to path format
     self.debug_path = [ghost_pos, move_choice]
     return self.debug_path
    
    def get_neighbors(self, pos, maze):
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] != 1:
                neighbors.append((nx, ny))
        return neighbors
    
    def distance(self, pos1, pos2):
        return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
    
    def move_random(self, maze):
        possible_directions = []
        grid_pos = self.get_grid_position()
        
        for direction in [UP, DOWN, LEFT, RIGHT]:
            new_pos = (
                grid_pos[0] + direction[0],
                grid_pos[1] + direction[1]
            )
            
            if (0 <= new_pos[0] < COLS and 0 <= new_pos[1] < ROWS and
                maze[new_pos[1]][new_pos[0]] != 1 and
                direction != (-self.direction[0], -self.direction[1])):
                possible_directions.append(direction)
        
        if possible_directions:
            self.direction = random.choice(possible_directions)
    
    def get_chase_target(self, pacman, other_ghosts):
        if not self.active:
            return self.exit_position
            
        pacman_pos = pacman.get_grid_position()
        pacman_dir = pacman.direction
        
        if self.name == "blinky":
            return pacman_pos
        elif self.name == "pinky":
            if pacman_dir == STOP:
                return pacman_pos
            
            target = (
                pacman_pos[0] + pacman_dir[0] * 4,
                pacman_pos[1] + pacman_dir[1] * 4
            )
            
            return (
                max(0, min(target[0], COLS - 1)),
                max(0, min(target[1], ROWS - 1))
            )
        elif self.name == "inky":
            if pacman_dir == STOP:
                return pacman_pos
            
            pivot = (
                pacman_pos[0] + pacman_dir[0] * 2,
                pacman_pos[1] + pacman_dir[1] * 2
            )
            
            blinky_pos = None
            for ghost in other_ghosts:
                if ghost.name == "blinky" and ghost.active:
                    blinky_pos = ghost.get_grid_position()
                    break
            
            if blinky_pos is None:
                return pivot
            
            vector = (pivot[0] - blinky_pos[0], pivot[1] - blinky_pos[1])
            
            target = (
                blinky_pos[0] + vector[0] * 2,
                blinky_pos[1] + vector[1] * 2
            )
            
            return (
                max(0, min(target[0], COLS - 1)),
                max(0, min(target[1], ROWS - 1))
            )
        elif self.name == "clyde":
            distance = abs(pacman_pos[0] - self.get_grid_position()[0]) + \
                      abs(pacman_pos[1] - self.get_grid_position()[1])
            
            if distance > 8:
                return pacman_pos
            else:
                return self.scatter_target
    
    def draw(self, screen):
        if not self.active:
            return
            
        self.animation_frame += 1
        
        if self.mode == "frightened":
            if self.frightened_timer < 60 and self.animation_frame % 10 < 5:
                color = WHITE
            else:
                color = FRIGHTENED_COLOR
        elif self.mode == "eaten":
            color = GRAY
        else:
            color = self.color
        
        if self.mode != "eaten":
            pygame.draw.circle(screen, color, 
                              (int(self.position[0]), int(self.position[1])), 
                              self.radius)
            
            points = []
            for i in range(5):
                x = self.position[0] - self.radius + (i * self.radius * 2 / 4)
                y_offset = math.sin(self.animation_frame * 0.1 + i) * 3
                points.append((x, self.position[1] + self.radius + y_offset))
            
            points.append((self.position[0] + self.radius, self.position[1] + self.radius))
            points.append((self.position[0] - self.radius, self.position[1] + self.radius))
            
            pygame.draw.polygon(screen, color, points)
        
        eye_radius = self.radius // 3
        left_eye_pos = (self.position[0] - self.radius // 2, self.position[1] - self.radius // 3)
        right_eye_pos = (self.position[0] + self.radius // 2, self.position[1] - self.radius // 3)
        
        pygame.draw.circle(screen, WHITE, (int(left_eye_pos[0]), int(left_eye_pos[1])), eye_radius)
        pygame.draw.circle(screen, WHITE, (int(right_eye_pos[0]), int(right_eye_pos[1])), eye_radius)
        
        pupil_offset = eye_radius // 2
        if self.eye_direction == LEFT:
            left_pupil = (left_eye_pos[0] - pupil_offset, left_eye_pos[1])
            right_pupil = (right_eye_pos[0] - pupil_offset, right_eye_pos[1])
        elif self.eye_direction == RIGHT:
            left_pupil = (left_eye_pos[0] + pupil_offset, left_eye_pos[1])
            right_pupil = (right_eye_pos[0] + pupil_offset, right_eye_pos[1])
        elif self.eye_direction == UP:
            left_pupil = (left_eye_pos[0], left_eye_pos[1] - pupil_offset)
            right_pupil = (right_eye_pos[0], right_eye_pos[1] - pupil_offset)
        elif self.eye_direction == DOWN:
            left_pupil = (left_eye_pos[0], left_eye_pos[1] + pupil_offset)
            right_pupil = (right_eye_pos[0], right_eye_pos[1] + pupil_offset)
        else:
            left_pupil = left_eye_pos
            right_pupil = right_eye_pos
        
        pygame.draw.circle(screen, BLACK, (int(left_pupil[0]), int(left_pupil[1])), eye_radius // 2)
        pygame.draw.circle(screen, BLACK, (int(right_pupil[0]), int(right_pupil[1])), eye_radius // 2)
    
    def get_grid_position(self):
        return (int(self.position[0] // GRID_SIZE), int(self.position[1] // GRID_SIZE))
    
    def reset(self):
        self.position = list(self.initial_position)
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.mode = "scatter"
        self.mode_timer = self.scatter_duration * 60
        self.frightened_timer = 0
        self.in_house = True
        self.speed = self.initial_speed
    
    def set_frightened(self, duration):
        if self.active:
            self.mode = "frightened"
            self.frightened_timer = duration
            self.speed = self.frightened_speed
    
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def draw_debug(self, screen):
     if not hasattr(self, 'debug_open_set') or not hasattr(self, 'debug_closed_set'):
        return
    
     # Debug Interface
     debug_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
     if hasattr(self, 'debug_open_set'):
        for pos in self.debug_open_set:
            rect = pygame.Rect(
                pos[0] * GRID_SIZE + 2,
                pos[1] * GRID_SIZE + 2,
                GRID_SIZE - 4,
                GRID_SIZE - 4
            )
            pygame.draw.rect(debug_surface, (100, 100, 255, 128), rect) 
    
     if hasattr(self, 'debug_closed_set'):
        for pos in self.debug_closed_set:
            rect = pygame.Rect(
                pos[0] * GRID_SIZE + 2,
                pos[1] * GRID_SIZE + 2,
                GRID_SIZE - 4,
                GRID_SIZE - 4
            )
            pygame.draw.rect(debug_surface, (255, 100, 100, 128), rect) 
    
     if hasattr(self, 'debug_path') and self.debug_path:
        for i in range(len(self.debug_path) - 1):
            start_pos = (
                self.debug_path[i][0] * GRID_SIZE + GRID_SIZE // 2,
                self.debug_path[i][1] * GRID_SIZE + GRID_SIZE // 2
            )
            end_pos = (
                self.debug_path[i+1][0] * GRID_SIZE + GRID_SIZE // 2,
                self.debug_path[i+1][1] * GRID_SIZE + GRID_SIZE // 2
            )
            pygame.draw.line(screen, GREEN, start_pos, end_pos, 3)
    
     screen.blit(debug_surface, (0, 0))