from pygame import transform, image, display
import pygame

# Initialise pygame
pygame.init()
screen = display.set_mode((800, 800))

class Icon:

    def __init__(self, position: tuple, image_file: str, scale: float) -> None:

        temp_image = image.load(image_file).convert_alpha()
        self.image = transform.scale_by(temp_image, scale)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.position = position
        self.scale = scale
        self.is_visible = True

    # Procedure to draw image onto the screen

    def draw(self, screen: display) -> None:

        screen.blit(self.image, ((self.position[0] - self.width / 2), (self.position[1] - self.height / 2)))