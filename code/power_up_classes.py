from pygame import Rect, image, transform, mask, display
from random import randint, choice
from math import sqrt
import pygame

# Initialise pygame
pygame.init()
screen = display.set_mode((800, 800))

# Power up class to contain all the different power up effects:

class PowerUp:

    def __init__(self, half_dimensions: tuple, player: str) -> None:

        self.is_active = False
        self.player = player

        self.despawn = True

        self.images = {"freeze": "icons/Power Ups/freeze.png",
                       "shot_stopper": "icons/Power Ups/shot_stopper.png",
                       "widen_goal": "icons/Power Ups/widen_goal.png",
                       "double_points": "icons/Power Ups/double_points.png",
                       "power_shot": "icons/Power Ups/power_shot.png",
                       "enlarge_paddle": "icons/Power Ups/enlarge_paddle.png"}
        
        self.image = None

        self.power_up = None
        self.power_ups = ["freeze", "shot_stopper", "widen_goal", "double_points", "power_shot", "enlarge_paddle"]

        # This will determine which part of the table that the power up can spawn in
        self.half_dimensions = half_dimensions

        # The power ups will be a circle of radius 15 - we will create a rectangular hitbox around the power up
        self.rect = Rect(0, 0, 30, 30)

        self.x = None
        self.y = None

        self.test = False

    # Randomise the power up to be given and its spawn position
    def randomise_spawn(self) -> None:

        if self.test:

            print("*** TEST MODE ***")
            self.power_up = "power_shot"

        elif not self.test:

            # Choose a random power up from the selection:
            self.power_up = choice(self.power_ups)

        # Load the corresponding image and scale accordingly
        image = image.load(self.images[self.power_up])
        self.image = transform.scale(image, (30, 30))

        # Randomly generate coordinates to spawn the power up in, accouting for the power up dimensions and walls of the table
        self.x = randint(int(self.half_dimensions[0] + 10 + 15), int(self.half_dimensions[1] - 10 - 15))
        self.y = randint(int(self.half_dimensions[2] + 10 + 15), int(self.half_dimensions[3] - 15))

        # Reposition the hitbox of the power up and display the power up on the screen
        self.rect.center = (self.x, self.y)

    # Draw the power up on the screen
    def draw(self, screen: display) -> None:

        screen.blit(self.image, (self.x - 15, self.y - 15))

    # Subroutine to collect the power up:
    def collect(self, Paddle: object) -> None:

        paddle_x, paddle_y = Paddle.rect.center
        distance = sqrt( (self.x - paddle_x) ** 2 + (self.y - paddle_y) ** 2)

        # If the paddle intersects the power_up, then it has been collected
        if distance < Paddle.width / 2 + 15:

            self.is_active = True
        
        else:

            self.is_active = False

    def freeze(self, Paddle: object, optional=None) -> None:
        
        if self.is_active:

            Paddle.frozen = True

        else:

            Paddle.frozen = False

    def double_points(self, Scoreboard: object, optional=None) -> None:

        if not self.is_active:

            Scoreboard.p_multiplier = 1
            Scoreboard.comp_multiplier = 1

        elif self.is_active:

            if self.player == "player":

                Scoreboard.comp_multiplier = 2

            elif self.player == "computer":

                Scoreboard.p_multiplier = 2

    # Subroutine to widen the goal if widen goal power up is active

    def widen_goal(self, Goal: object, optional=None) -> None:

        # Change the dimensions and hitbox of the goal if active
        if self.is_active:

            Goal.width = 300
            Goal.rect = Rect(Goal.x - Goal.width / 2, Goal.y, Goal.width, 100)
            Goal.mask = mask.Mask((Goal.rect.width, Goal.rect.height), True)
            
            if Goal.player == "computer":

                Goal.left_corner = (Goal.rect.left, Goal.rect.bottom)
                Goal.right_corner = (Goal.rect.right, Goal.rect.bottom)

            elif Goal.player == "player":

                Goal.left_corner = (Goal.rect.left, Goal.rect.top)
                Goal.right_corner = (Goal.rect.right, Goal.rect.top)

        # If this power up is not active, then reset the goal's hitbox
        if not self.is_active:

            Goal.width = 150
            Goal.rect = Rect(Goal.x - Goal.width / 2, Goal.y, Goal.width, 100)
            Goal.mask = mask.Mask((Goal.rect.width, Goal.rect.height), True)
            
            if Goal.player == "computer":

                Goal.left_corner = (Goal.rect.left, Goal.rect.bottom)
                Goal.right_corner = (Goal.rect.right, Goal.rect.bottom)

            elif Goal.player == "player":

                Goal.left_corner = (Goal.rect.left, Goal.rect.top)
                Goal.right_corner = (Goal.rect.right, Goal.rect.top)

    def enlarge_paddle(self, Paddle: object, optional=None) -> None:

        # If the power up is active, enlarge the hitbox of the paddle
        if self.is_active:

            Paddle.image = transform.scale2x(Paddle.image)
            Paddle.width = Paddle.image.get_width()
            Paddle.height = Paddle.image.get_height()

        # Otherwise, rescale the paddle's hitbox to what it was originally
        if not self.is_active:

            Paddle.image = transform.scale_by(Paddle.image, 0.5)
            Paddle.width = Paddle.image.get_width()
            Paddle.height = Paddle.image.get_height()

    def shot_stopper(self, Paddle: object, Puck: object, Goal: object, Scoreboard: object, glows: list) -> None:

        if self.is_active:

            Puck.glow_colour = glows[Paddle.colour]
            Goal.display = False
            
            # For the active player, double points if they score in the opponents goal while active
            if Goal.player == "computer":

                Scoreboard.p_multiplier = 2

            if Goal.player == "player":

                Scoreboard.comp_multiplier = 2
        
        elif not self.is_active:

            # Reset to defaults

            Puck.glow_colour = (0, 0, 0, 0)
            Scoreboard.comp_multiplier = 1
            Scoreboard.p_multiplier = 1
            Goal.display = True
        
    def power_shot(self, Paddle: object, optional=None) -> None:

        if self.is_active:

            Paddle.power_shot = True

        elif not self.is_active:

            Paddle.power_shot = False     