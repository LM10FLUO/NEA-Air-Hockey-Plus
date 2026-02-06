from math import inf
from numpy import full
from pygame import Rect, draw, display, mask
import pygame
from random import randint



class GridSquare:

    def __init__(self, position: tuple):

        self.position = position

        self.is_obstacle: bool = False
        self.is_target: bool = False
        self.is_start: bool = False
        self.is_discovered: bool = False
        self.is_path: bool = False
        self.weight: int = 50
        self.weight_decreased: bool = False
        self.is_perm_obstacle: bool = False

        self.colour = (255,255,255)

        # We will initially set all undiscovered nodes to have infinite weight
        self.f_cost: float = inf
        self.g_cost: float = inf
        self.h_cost: float = inf

        self.pointer = full(2, None)
        self.neighbours = []

        # Each grid square will be 5x5 pixels in dimension
        self.rect = Rect(position[0] * 10, position[1] * 10, 10, 10)
        self.mask = mask.Mask((self.rect.width, self.rect.height))
        self.mask.fill()

    def draw(self, screen: display) -> None:

        if not self.is_obstacle and not self.is_start and not self.is_discovered and not self.is_target and not self.is_path and not self.is_perm_obstacle:# and not self.weight_decreased:

            draw.rect(screen, self.colour, self.rect)
            draw.rect(screen, (0,0,0), self.rect, 1)
        
        else:

            if self.is_obstacle or self.is_perm_obstacle:
                self.colour = (0,0,0)   # BLACK

            elif self.is_target:
                self.colour = (255, 0, 0)   # GREEN

            elif self.is_start:
                self.colour = (255, 0, 0)   # RED
            
            elif self.is_discovered:
                self.colour = (0, 0, 255)   # BLUE

            elif self.is_path:
                self.colour = (0, 255, 0)   # GREEN

            # elif self.weight_decreased:
            #     self.colour = (0, 255, 0)   # GREEN

            draw.rect(screen, (0,0,0), self.rect, 1)
            draw.rect(screen, self.colour, self.rect)

    # Procedure to reset the weights and flags of the square

    def reset(self):

        self.is_obstacle = False
        self.is_target = False
        self.is_start = False
        self.is_discovered = False
        self.is_path = False
        self.weight = 50
        self.weight_decreased = False

        self.colour = (255,255,255)

        # We will initially set all undiscovered nodes to have infinite weight
        self.f_cost= inf
        self.g_cost= inf
        self.h_cost = inf

        self.pointer = full(2, None)



# Setting up the grid for pathfinding 

def create_grid(table_height: int, table_width: int) -> list:
    
    grid = []

    # We will use grids that are 10x10 pixels in dimension

    rows = int(table_height / 10)
    columns = int(table_width / 10)    

    for row_number in range(rows):
        
        row = []

        for column_number in range(columns):

            row.append(GridSquare((row_number, column_number)))
            
            # Identify neighbours of each square
            max_row = row_number
            min_row = row_number
            max_column = column_number
            min_column = column_number

            if (row_number + 1) < rows:
                max_row += 1

            if (row_number) - 1 >= 0:
                min_row -= 1

            if (column_number + 1) < rows:
                max_column += 1

            if (column_number) - 1 >= 0:
                min_column -= 1

            # Store each neighbour
            for j in range(min_row, (max_row + 1)):

                for i in range(min_column, max_column + 1):

                    # Make sure we don't append the actual square into its neighbours
                    if j == row_number and i == column_number:

                        continue

                    else:

                        row[column_number].neighbours.append((j, i))

            # # For testing, randomly generate obstacles
            # random_num = randint(0,10)

            # if random_num == 1:
            #     row[column_number].is_obstacle = True

        grid.append(row)

    return grid



if __name__ == "__main__":

    grid = create_grid(800, 800)

    # Initialise pygame
    pygame.init()
    screen = display.set_mode((800, 800))
    display.set_caption("Grid Testing")
    screen.fill((255,255,255))

    while True:

        for row in grid:

            for square in row:

                square.draw(screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

        pygame.display.update()