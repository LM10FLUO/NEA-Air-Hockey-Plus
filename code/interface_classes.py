from pygame import init, display, image, transform
import pygame
from sys import exit
from random import randint

# Initialise pygame
init()
screen = display.set_mode((800, 800))

# Class to display the appropriate screens:

class Interface_Screens:

    def __init__(self, title_path: str, settings_path: str, loss_path: str, win_path: str, height: int) -> None:

        title_background = image.load("interface_screens/Air_Hockey_Home_Screen.png")

        # Rescale the title screen image so that it fits the screen correctly
        title_height = title_background.get_height()
        scale = height / title_height

        self.title_background = transform.scale_by(title_background, scale)

        settings_background = image.load("interface_screens/Settings_Screen.png")

        # Rescale the title screen image so that it fits the screen correctly
        settings_height = settings_background.get_height()
        scale = height / settings_height
        self.settings_background = transform.scale_by(settings_background, scale)

        win_background = image.load("interface_screens/Winning_Screen.png")

        # Rescale the title screen image so that it fits the screen correctly
        win_height = win_background.get_height()
        scale = height / win_height

        self.win_background = transform.scale_by(win_background, scale)

        loss_background = image.load("interface_screens/Losing_Screen.png")

        # Rescale the title screen image so that it fits the screen correctly
        loss_height = loss_background.get_height()
        scale = height / loss_height

        self.loss_background = transform.scale_by(loss_background, scale)

    def display_title(self, screen: display) -> None:

        screen.fill((249, 244, 235))
        screen.blit(self.title_background, (400 - (self.title_background.get_width() / 2), 0))

    def display_settings(self, screen: display) -> None:

        screen.fill((249, 244, 235))
        screen.blit(self.settings_background, (400 - (self.settings_background.get_width() / 2), 0))

    def display_loss(self, screen: display) -> None:

        screen.fill((249, 244, 235))
        screen.blit(self.loss_background, (400 - (self.loss_background.get_width() / 2), 0))

    def display_win(self, screen: display) -> None:

        screen.fill((249, 244, 235))
        screen.blit(self.win_background, (400 - (self.win_background.get_width() / 2), 0))

if __name__ == "__main__":

    Interface = Interface_Screens(title_path="interface_screens/Air_Hockey_Home_Scree.png",
                                  settings_path="interface_screens/Settings_Screen.png",
                                  loss_path="interface_screen/Losing_Screen.png",
                                  win_path="interface_screens/Winning_Screen.png",
                                  height=800)
    

    while True:

        random = randint(1,4)

        if random == 1:

            Interface.display_title(screen)

        elif random == 2:

            Interface.display_settings(screen)

        elif random == 3:

            Interface.display_loss(screen)

        else:

            Interface.display_win(screen)

        display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

                

