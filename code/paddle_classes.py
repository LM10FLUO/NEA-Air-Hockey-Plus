# Libraries
from pygame import mask, mouse, display
from numpy import array, round
from math import sqrt
import pygame

# Class to instantiate paddles from

# Initialise pygame
pygame.init()
screen = display.set_mode((800, 800))

class Paddle:

    def __init__(self, image, colour: str) -> None:

        self.image = image
        self.colour = colour
        self.rect = self.image.get_rect()
        self.mask = mask.from_surface(self.image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity = array([0, 0])
        self.initial_pos = array([0,0])
        self.final_pos = array([0,0])

        # Flag to disable movement if frozen:
        self.frozen = False

        # Flag to check if the power shot power up is active
        self.power_shot = False
        self.position_reset = False

    # Procedure to move the paddle on the screen based on the user's mouse placement

    def move_paddle(self, screen: display, table_dimensions: tuple) -> None:

        # If the paddle is frozen, fix the paddle to its most recent position
        if self.frozen:

            print("frozen")
            draw_pos = self.final_pos
            self.velocity = array([0, 0])

        elif not self.frozen:

            table_width, table_height = table_dimensions

            mouse_pos = mouse.get_pos()

            # Convert to an array to make the position mutable
            draw_pos = array([mouse_pos[0], mouse_pos[1]])

            # Ensure that the paddle is drawn only in a valid position
            # n.b. /2 is for the radial length

            if mouse_pos[0] < (5 + int(self.width/2)):
                draw_pos[0] = 5 + self.width / 2 

            elif mouse_pos[0] > (table_width - int(self.width / 2) - 5):
                draw_pos[0] = (table_width - int(self.width / 2) - 5)

            if mouse_pos[1] < (table_height / 2 + int(self.width / 2)):
                draw_pos[1] = (table_height / 2 + int(self.width / 2))

            elif mouse_pos[1] > (table_height - int(self.width / 2)):
                draw_pos[1] = (table_height - int(self.width / 2))

        # Ensure that the rectangular hitbox of the paddle aligns with the position of the paddle image currently
        self.rect.center = tuple(draw_pos)

        screen.blit(self.image, (draw_pos[0]-self.width/2, draw_pos[1]-self.height/2))

    def determine_vel(self) -> None:

        # If the paddle is not frozen, then calculate the paddle's speed
        if not self.frozen:

            # Calculate the time that a frame lasts (n.b. 60 fps)
            dt = 1 / 60

            # We will use vector properties to simplify and speed up calculations using numpy arrays

            # Calculate the change in the x and y positions and calculate the instantaneous velocity of the paddle
            dx_dy = self.final_pos - self.initial_pos

            self.velocity = dx_dy / dt

            # Ensure that the velocity is an integer number
            self.velocity = round(self.velocity, decimals=0)

            if self.power_shot == True:

                self.velocity = self.velocity * 2

            self.initial_pos = self.final_pos
            self.final_pos = array(list(mouse.get_pos())) # Convert back into an array for calculations

    def check_puck_collision(self, Puck: object) -> bool:

        x_pos, y_pos = self.rect.center
        paddle_radius = self.width / 2
        puck_x, puck_y = Puck.rect.center
        puck_radius = Puck.width / 2

        distance = sqrt((puck_x - x_pos)**2 + (puck_y - y_pos)**2)

        if distance <= (puck_radius + paddle_radius):

            return True
        
        else:

            return False