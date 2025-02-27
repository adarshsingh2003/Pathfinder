import heapq
import numpy as np
import pygame

from pygame.locals import (
    K_BACKSPACE,
    K_RETURN,
    KEYDOWN,
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
    MOUSEMOTION,
    QUIT,
)


class Cell:
    def __init__(self, figure, is_wall, distance_from_start, coords, visited=False, predecessor=None):
        self.figure = figure
        self.is_wall = is_wall
        self.distance_from_start = distance_from_start
        self.coords = coords
        self.visited = visited
        self.predecessor = predecessor
    

    def __lt__(self, other_cell):
        return self.distance_from_start < other_cell.distance_from_start


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

NUMBER_OF_ROWS = WINDOW_HEIGHT // 10
NUMBER_OF_COLUMNS = WINDOW_WIDTH // 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)


def setup():
    screen.fill(BLACK)
    pygame.display.set_caption("Pathfinder")

    initialize_matrix()
    draw_grid()


def initialize_matrix():
    global matrix

    matrix = np.empty((NUMBER_OF_ROWS, NUMBER_OF_COLUMNS), dtype=Cell)


def draw_grid():
    global start_coords, end_coords

    MARGIN = 1
    DIMENSION = (WINDOW_WIDTH - MARGIN * NUMBER_OF_COLUMNS) // NUMBER_OF_COLUMNS

    for x in range(NUMBER_OF_ROWS):
        for y in range(NUMBER_OF_COLUMNS):
            rect = pygame.Rect((MARGIN + DIMENSION) * y + MARGIN, (MARGIN + DIMENSION) * x + MARGIN, DIMENSION, DIMENSION)
            pygame.draw.rect(screen, WHITE, rect)
            matrix[x][y] = Cell(rect.copy(), False, np.inf, (x, y))
    
    start_coords = (np.random.randint(0, NUMBER_OF_ROWS), np.random.randint(0, NUMBER_OF_COLUMNS))
    end_coords = (np.random.randint(0, NUMBER_OF_ROWS), np.random.randint(0, NUMBER_OF_COLUMNS))
    
    while start_coords == end_coords:
        end_coords = (np.random.randint(0, NUMBER_OF_ROWS), np.random.randint(0, NUMBER_OF_COLUMNS))

    start_cell = matrix[start_coords[0]][start_coords[1]]
    end_cell = matrix[end_coords[0]][end_coords[1]]

    start_rect = start_cell.figure
    end_rect = end_cell.figure

    pygame.draw.rect(screen, BLUE, start_rect)
    pygame.draw.rect(screen, RED, end_rect)

    matrix[start_coords[0]][start_coords[1]] = Cell(start_rect.copy(), True, 0, start_coords, visited=True)
    matrix[end_coords[0]][end_coords[1]] = Cell(end_rect.copy(), False, np.inf, end_coords)
    
    pygame.display.update()


def mark_as_wall():
    position = pygame.mouse.get_pos()
    col = position[0] // 10
    row = position[1] // 10

    start_cell = matrix[start_coords[0]][start_coords[1]]
    end_cell = matrix[end_coords[0]][end_coords[1]]

    if matrix[row][col] != start_cell and matrix[row][col] != end_cell:
        matrix[row][col].is_wall = True
        rect = matrix[row][col].figure
        pygame.draw.rect(screen, BLACK, rect)
        
        pygame.display.update()


def mark_as_visited(cell, distance, predecessor):
    end_cell = matrix[end_coords[0]][end_coords[1]]

    if distance < cell.distance_from_start:
        cell.distance_from_start = distance
        cell.visited = True
        cell.predecessor = predecessor

        if cell != end_cell:
            rect = cell.figure
            pygame.draw.rect(screen, YELLOW, rect)

            pygame.display.update()
            
            return False
    
    return True


def highlight_path():
    end_cell = matrix[end_coords[0]][end_coords[1]]
    current = end_cell.predecessor
    start = matrix[start_coords[0]][start_coords[1]]

    while current != start:
        rect = current.figure
        pygame.draw.rect(screen, GREEN, rect)

        pygame.display.update()

        current = current.predecessor


def find_path():
    start = matrix[start_coords[0]][start_coords[1]]
    queue = [start]
    found = True
    
    while queue:
        most_near = heapq.heappop(queue)
        
        if most_near.distance_from_start == np.inf:
            found = False
            break

        i, j = most_near.coords
        new_distance = most_near.distance_from_start + 1
        above = matrix[i-1][j] if 0 <= i-1 < NUMBER_OF_ROWS else None
        below = matrix[i+1][j] if 0 <= i+1 < NUMBER_OF_ROWS else None
        right = matrix[i][j+1] if 0 <= j+1 < NUMBER_OF_COLUMNS else None
        left = matrix[i][j-1] if 0 <= j-1 < NUMBER_OF_COLUMNS else None

        if above and not above.is_wall and not above.visited:
            if mark_as_visited(above, new_distance, most_near):
                break
            heapq.heappush(queue, above)
        
        if below and not below.is_wall and not below.visited:
            if mark_as_visited(below, new_distance, most_near):
                break
            heapq.heappush(queue, below)

        if right and not right.is_wall and not right.visited:
            if mark_as_visited(right, new_distance, most_near):
                break
            heapq.heappush(queue, right)

        if left and not left.is_wall and not left.visited: 
            if mark_as_visited(left, new_distance, most_near):
                break
            heapq.heappush(queue, left)
        
        if all(value for value in [above != None, below != None, right != None, left != None]):
            if all(value for value in [above.is_wall, below.is_wall, right.is_wall, left.is_wall]):
                return

    
    if found:
        highlight_path()
    

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
matrix = None
start_coords = None
end_coords = None

setup()

pygame.init()

running = True
dragging = False

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if event.type == MOUSEBUTTONDOWN:
            dragging = True
        
        if dragging and event.type == MOUSEMOTION:
            mark_as_wall()
        
        if event.type == MOUSEBUTTONUP:
            dragging = False
        
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                find_path()
            if event.key == K_BACKSPACE:
                setup()
       
pygame.quit()