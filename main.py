# Libraries
import pygame
import numpy
from sys import exit

# Constants
WIDTH, HEIGHT = (800, 840)
GREY = (235, 235, 235)
CREAM = (247, 242, 239)

# Flags
title = True
settings = False
game = False

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Hockey Plus")

# Displays title screen

def display_title():

    # Load the image for the title screen
    title_surface = pygame.image.load("Air hockey home screen.png")

    # Rescale the title screen image so that it fits the screen correctly
    title_width, title_height = title_surface.get_size()
    scale = HEIGHT / title_height
    title_surface = pygame.transform.scale_by(title_surface, scale)

    # Match the backdrop colour to the title screen colour
    screen.fill(CREAM)

    # Position the title screen image in the centre
    screen.blit(title_surface, (400 - (title_width * scale / 2), 0))

# Main game loop
if __name__ == "__main__":

    while True:

        # Title screen loop
        while title == True:
            
            # Testing 
            print("entered title loop")
            
            display_title()

            # Handle quitting the game screen  
            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:

                        title = False

            pygame.display.update()

        # Testing
        print("spacebar pressed - title loop has been broken")

        # Handle quitting the game screen  
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

