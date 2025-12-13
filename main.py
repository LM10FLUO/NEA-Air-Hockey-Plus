# Libraries
import pygame
import numpy as np
from sys import exit

# Constants
WIDTH, HEIGHT = (800, 840)
GREY = (235, 235, 235)
CREAM = (249, 244, 235)
RED = (214, 73, 59)
HAND_CURSOR = pygame.SYSTEM_CURSOR_HAND
POINTER_CURSOR = pygame.SYSTEM_CURSOR_ARROW
TEXT_CURSOR = pygame.SYSTEM_CURSOR_IBEAM

# Flags
run_title: bool = True
run_settings: bool = False
run_game: bool = False
run_end: bool = False
difficulty: int = 1
paddle_colour: int = 0
max_score: int = 10
first_run: bool = True

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Hockey Plus")
clock = pygame.time.Clock()


# Displays title screen

def display_title(screen) -> None:

    # Load the image for the title screen
    title_surface = pygame.image.load("interface_screens/Air hockey home screen.png")

    # Rescale the title screen image so that it fits the screen correctly
    title_width, title_height = title_surface.get_size()
    scale = HEIGHT / title_height
    title_surface = pygame.transform.scale_by(title_surface, scale)

    # Match the backdrop colour to the title screen colour
    screen.fill(CREAM)

    # Position the title screen image in the centre
    screen.blit(title_surface, (400 - (title_width * scale / 2), 0))


# Display the background of the settings screen onto the screen

def display_settings(screen) -> None:

    # Fill the background colour to cream

    screen.fill((249, 244, 235))

    settings_background = pygame.image.load("interface_screens/settings_background.png")
    settings_width, settings_height = settings_background.get_size()
    scale = HEIGHT / settings_height
    title_surface = pygame.transform.scale_by(settings_background, scale)

    # Position centrally
    screen.blit(title_surface, (400 - (settings_width * scale / 2), 0))

# Display the table onto the screen

def display_table(screen) -> None:

    # Fill the background colour to cream

    screen.fill((249, 244, 235))

    table_image = pygame.image.load("interface_screens/table.png")
    table_height = table_image.get_height()
    scale = HEIGHT / table_height
    table_surface = pygame.transform.scale_by(table_image, scale)
    screen.blit(table_surface, (0,0))

# Check if the user has given a valid max score for them to proceed to the next screen

def validate_input(user_input) -> bool:

    if int(user_input) == 0:

        return False

    else:

        return True

# Button class to instantiate different clickable buttons from

class Button:

    def __init__(self, position: tuple, image_file: str, scale: float) -> None:

        # Load the image and scale the image down as intended
        image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale_by(image, scale)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.position = position
        self.clicked = False

        # Get the rectangular area of the image to determine whether user interacts with button
        self.rect = self.image.get_rect(center=self.position)
        

    # display the button on the screen and check for interaction

    def draw(self) -> bool:

        # Flag to check whether the user has interacted with the button
        active = False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if the user clicks on the button
        if self.rect.collidepoint(mouse_pos):

            if pygame.mouse.get_pressed()[0] and self.clicked == False: # if left mouse click

                self.clicked = True
                active = True

        if not pygame.mouse.get_pressed()[0]: # if mouse is not clicked

            self.clicked = False

        # Draw image on the screen (based on the centre of the object)
        screen.blit(self.image, ((self.position[0] - self.width / 2), (self.position[1] - self.height / 2)))

        return active

# Class container to instatiate image icons from

class Icon:

    def __init__(self, position: tuple, image_file: str, scale: float) -> None:

        image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale_by(image, scale)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.position = position
        self.scale = scale
        self.is_visible = True

    # Procedure to draw image onto the screen

    def draw(self) -> None:

        screen.blit(self.image, ((self.position[0] - self.width / 2), (self.position[1] - self.height / 2)))

# Class for textbox to take in user inputs for the score

class TextBox:

    def __init__(self, position: tuple, font_file: str, font_size: int, user_input: int = ""):

        self.position = position
        self.font = pygame.font.Font(font_file, font_size)
        self.user_input = user_input
        self.active = False

    def draw(self) -> None:

        # Render the text and check whether the user clicks on it to change it 
        text_display = self.font.render(self.user_input, True, RED, None)
        text_rect = text_display.get_rect()
        text_rect.center = (self.position[0], self.position[1])

        mouse_pos = pygame.mouse.get_pos()

        # If the mouse is hovers over and clicks the textbox, allow them to edit the text
        if text_rect.collidepoint(mouse_pos):

            # Change the mouse cursor if the input box is being hovered over to make it clearer
            pygame.mouse.set_cursor(TEXT_CURSOR)

            if pygame.mouse.get_pressed()[0] == True:

                self.active = True

        else:

            # If not being hovered over, change the mouse cursor back to normal
            pygame.mouse.set_cursor(POINTER_CURSOR)

            if pygame.mouse.get_pressed()[0] == True:

                self.active = False

        if self.active == True:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                        pygame.quit()
                        exit()

                if event.type == pygame.KEYDOWN:

                    # Only allow the user to input numbers
                    if event.unicode.isdigit() == True:

                            self.user_input += event.unicode

                    # Get rid of placeholder if new input is given
                    if self.user_input[0] == "0":

                        self.user_input = self.user_input[1:]

                    if event.key == pygame.K_BACKSPACE:

                        self.user_input = self.user_input[:-1]

                        # Use a placeholder value of 0 to indicate where the score can be inputted
                        if self.user_input == "":

                            self.user_input = "0"



            # If not being hovered over, change the mouse cursor back to normal


        screen.blit(text_display, ((self.position[0] - text_rect.width/2), (self.position[1] - text_rect.height/2)))

# Class to instantiate paddles from

class Paddle:

    def __init__(self, image) -> None:

        self.image = image
        self.rect = self.image.get_rect()

    def move_paddle(self) -> None:

        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.image, (mouse_pos[0]-self.rect.width/2, mouse_pos[1]-self.rect.height/2))


        

        

# Instatiating objects
Easy_Icon = Icon(position=(400, 292), image_file="icons/easy_icon.png", scale=0.5)
Medium_Icon = Icon(position=(400, 292), image_file="icons/medium_icon.png", scale=0.5)
Hard_Icon = Icon(position=(400, 292), image_file="icons/hard_icon.png", scale=0.5)

Easy_Letters = Icon(position=(400, 350), image_file="icons/easy_letters.png", scale=0.2)
Medium_Letters = Icon(position=(400, 350), image_file="icons/medium_letters.png", scale=0.2)
Hard_Letters = Icon(position=(401, 350), image_file="icons/hard_letters.png", scale=0.2)

Right_Difficulty = Button(position=(585, 292), image_file="buttons/right_arrow.png", scale=0.5)
Left_Difficulty = Button(position=(215, 292), image_file="buttons/left_arrow.png", scale=0.5)

Right_Paddle = Button(position=(585, 652), image_file="buttons/right_arrow.png", scale=0.5)
Left_Paddle = Button(position=(215, 652), image_file="buttons/left_arrow.png", scale=0.5)

Red_Paddle_Icon = Icon(position=(400, 652), image_file="icons/red_paddle.png", scale=0.5)
Blue_Paddle_Icon = Icon(position=(400, 652), image_file="icons/blue_paddle.png", scale=0.5)
Green_Paddle_Icon = Icon(position=(400, 652), image_file="icons/green_paddle.png", scale=0.5)
Purple_Paddle_Icon = Icon(position=(400, 652), image_file="icons/purple_paddle.png", scale=0.5)

Play_Button = Button(position=(400,768), image_file="buttons/play_button.png", scale=0.5)
        
Score_Input = TextBox(position=(400, 480), font_file="Fonts/Grand9K Pixel.ttf", font_size=50, user_input="10")

Paddles = [Red_Paddle_Icon, Blue_Paddle_Icon, Green_Paddle_Icon, Purple_Paddle_Icon]
Difficulties = [[Easy_Icon, Easy_Letters], [Medium_Icon, Medium_Letters], [Hard_Icon, Hard_Letters]]







# Main game loop
if __name__ == "__main__":

    while True:

        # Title screen loop
        while run_title == True:
            
            display_title(screen=screen)

            # Handle quitting the game screen  
            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:

                        run_title = False
                        run_settings = True


            pygame.display.update()
            clock.tick(60)

        # Settings screen loop
        while run_settings == True:

            display_settings(screen=screen)
            Score_Input.draw()

            # Display the selected difficulty and paddle icons
            
            for icon in Difficulties[difficulty]:
                icon.draw()

            Paddles[paddle_colour].draw()

            # Keep track of the current settings and check whether button has been clicked
            if Right_Difficulty.draw():

                if difficulty < 2:

                    difficulty += 1

            if Left_Difficulty.draw():

                if difficulty > 0:

                    difficulty -= 1

            if Right_Paddle.draw():

                if paddle_colour < 3:

                    paddle_colour += 1

            if Left_Paddle.draw():

                if paddle_colour > 0:

                    paddle_colour -= 1

            # If the play_button is pressed, validate inputs and proceed to the main game screen
            if Play_Button.draw():

                if validate_input(Score_Input.user_input) == True:
                    
                    run_settings = False
                    run_game = True
                    max_score = int(Score_Input.user_input)
                    
                else:

                    print("Please enter a valid max score that is greater than 0")

            #print(pygame.mouse.get_pos())

            # Handle quitting the game screen  
            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    exit()

            pygame.display.update()

            # We will be running the game at 60 fps
            clock.tick(60)

        while run_game == True:

            display_table(screen)
            
            # If the first run, instantiate the paddle, preventing reinstantiation every loop
            if first_run:

                paddle_image = Paddles[paddle_colour].image
                User_Paddle = Paddle(paddle_image)
                first_run = False

            User_Paddle.move_paddle()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    exit()

            pygame.display.update()

            # We will be running the game at 60 fps
            clock.tick(60)

        # Handle quitting the game screen  
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

