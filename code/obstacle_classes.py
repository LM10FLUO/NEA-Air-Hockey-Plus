from pygame import image, transform, mask, mouse, display, draw, mixer
from numpy import array, round, linalg, ndarray, dot, sign, full
from random import choice, randint
from math import sqrt
from itertools import chain
import pygame

import computer_classes
import goal_classes
import puck_classes
import grid_classes

# Initialise pygame
pygame.init()
screen = display.set_mode((800, 800))

# This class will inherit from the pygame sprite class 
class Obstacle:

    def __init__(self, image_file: str) -> None:

        image = pygame.image.load(image_file)

        # The obstacles will be 50 by 50, taking up 25 grid squares 
        self.image = pygame.transform.scale(image, (50, 50))

        self.rect = self.image.get_rect()
        self.mask = mask.from_surface(self.image)
        self.width = self.rect.width
        self.position = None

        self.squares_occupied = full(65, None)

    def spawn_obstacle(self, screen: display, grid: list, Puck: object, Paddle: object, Computer_Goal: object, half_dimensions: tuple) -> None:

        self.squares_occupied = full(100, None)
        # First we need to determine the possible valid positions that we can spawn the obstacle in
        # We need to note that the obstacle has dimensions of 3 grid squares x 3 grid squares

        half_width, half_height = half_dimensions
        temp_grid = grid_classes.create_grid(half_width, half_height)

        last_row = half_height // 10
        last_column = half_width // 10 

        counter = 0
        valid_positions = full(10000, None)

        for i, row in enumerate(temp_grid):

            for j, square in enumerate(row):

                obstacle_found = False

                # If the square is occupied by an object on the table, we cannot spawn the obstacle on top of it
                # For accuracy, we be using mask collisions

                # First check for rect collisions as they are quicker
                if square.rect.colliderect(Puck.rect):

                    if Puck.mask.overlap(other=square.mask, offset=(square.rect.x - Puck.rect.x, square.rect.y - Puck.rect.y)):

                        square.is_obstacle = True
                        obstacle_found = True

                elif square.rect.colliderect(Paddle.rect):

                    if Paddle.mask.overlap(other=square.mask, offset=(square.rect.x - Paddle.rect.x, square.rect.y - Paddle.rect.y)):

                        square.is_obstacle = True
                        obstacle_found = True

                elif square.rect.colliderect(Computer_Goal.rect):

                    square.is_obstacle = True
                    obstacle_found = True

                # We can't spawn any objects in this region because of the dimensions of the object
                if j >= last_column - 4 or i >= last_row - 4:

                    square.is_obstacle = True

                # Account for the dimensions of the obstacle by considering collision space
                if obstacle_found:

                    for x in range(square.position[0] - 4, min(last_row, square.position[0] + 1)):

                        for y in range(max(0, square.position[1] - 4), square.position[1]):

                            temp_grid[x][y].is_obstacle = True

        for row in temp_grid:

            for square in row:

                if not square.is_obstacle:

                    valid_positions[counter] = square
                    counter += 1

        # Now out of the valid squares we can randomly pick a position to spawn the obstacles in 

        random_number = randint(0, counter-1)
        random_square = valid_positions[random_number]

        self.position = (random_square.position[0] * 10, random_square.position[1] * 10)
        self.rect.topleft = tuple(self.position)
    
        # Now we need to set the collision space of the obstacles
        index = 0
        additional_collision = ((Paddle.rect.width + 10) / 2) // 10 

        min_row = max(0, random_square.position[0] - additional_collision)
        max_row = min(random_square.position[0] + additional_collision + 5, last_column)

        min_column = max(0, random_square.position[1] - additional_collision)
        max_column = min(random_square.position[1] + additional_collision + 5, last_row)

        for j in range(int(min_row), int(max_row)):

            for i in range(int(min_column), int(max_column)):

                # If it is already a permanent obstacle, do not add it to the squares occupied as it will lead to reset problems
                if not grid[j][i].is_perm_obstacle:

                    grid[j][i].is_perm_obstacle = True
                    self.squares_occupied[index] = grid[j][i]
                    index += 1


    def draw(self, screen: display) -> None:

        screen.blit(self.image, self.position)

    def reset(self) -> None:

        index = 0

        while index < len(self.squares_occupied) and self.squares_occupied[index] is not None:

            # grid[self.squares_occupied[0]][self.squares_occupied[1]].is_perm_obstacle = False
            
            self.squares_occupied[index].is_perm_obstacle = False
            index += 1


if __name__ == "__main__":

    grid = grid_classes.create_grid(800, 800)

    # Initialise pygame
    pygame.init()
    screen = display.set_mode((800, 800))
    display.set_caption("Grid Testing")
    screen.fill((255,255,255))

    Computer = computer_classes.Computer_Hard("icons/red_paddle.png", (800, 800))
    Puck = puck_classes.Puck("red_puck.png", 0.4, (800, 800))
    Computer_Goal = goal_classes.Goal(281, -90, "computer")
    Player_Goal = goal_classes.Goal(281, 780, "player")
    Obstacle_ = Obstacle("icons/Obstacles/Obstacle.png")

    Puck.position = array([300, 300])
    counter = 0


    grid = grid_classes.create_grid(400, 400)
    counter = 0


    while True:

        screen.fill((255, 255, 255))

        if counter % 6000 == 0:

            for row in grid:

                for square in row:

                    square.reset()

            Obstacle_.reset()

            Obstacle_.spawn_obstacle(screen, grid, Puck, Computer, Computer_Goal, (400, 400))

            # Obstacle_.draw(screen)

        for row in grid:

            for square in row:

                square.draw(screen)

        Obstacle_.draw(screen)


        Computer.draw(screen)
        Puck.test_puck(screen)
        print(Puck.check_obstacle_collision(Obstacle_))
        # Player_Goal.draw(screen)

        counter += 1

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

        pygame.display.update()


            
