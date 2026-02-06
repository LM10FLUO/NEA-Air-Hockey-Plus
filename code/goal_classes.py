from pygame import Rect, mask, draw, display
import pygame

# Initialise pygame
pygame.init()
screen = display.set_mode((800, 800))

class Goal:

    def __init__(self, x: int, y: int, player: str) -> None:

        self.width = 150
        self.x = x
        self.y = y
        self.player = player

        self.rect = Rect(self.x - self.width / 2, self.y, self.width, 100)
        self.mask = mask.Mask((self.rect.width, self.rect.height), True)

        # Flag to check whether the goal is open
        self.display = True

        if self.player == "computer":

            self.left_corner = (self.rect.left, self.rect.bottom)
            self.right_corner = (self.rect.right, self.rect.bottom)

        elif self.player == "player":

            self.left_corner = (self.rect.left, self.rect.top)
            self.right_corner = (self.rect.right, self.rect.top)
        

    def draw(self, screen: display) -> None:

        if self.display:

            draw.rect(screen, (255,0,0), self.rect)

    # Function to check and determine who has scored a goal
    def check_goal(self, Puck: object) -> str:

        # Handle the cases of the computer goal and user goal separately
        if self.player == "computer":

            # Check if the puck collides with the goal and at least half the puck has entered the goal
            if Puck.rect.center[1] <= 5 and Puck.rect.left > self.rect.left and Puck.rect.right < self.rect.right:

                return "computer"
            
            else:

                return None
        
        if self.player == "player":

            # Check if the puck collides with the goal and the entirety of the puck lies into the goal
            if Puck.rect.center[1] >= 835 and Puck.rect.left > self.rect.left and Puck.rect.right < self.rect.right:

                return "player"
            
            else:

                return None