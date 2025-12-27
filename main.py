# Libraries
import pygame
import numpy as np
from sys import exit
from math import sqrt
from time import sleep

# Audio setup
pygame.mixer.init()
collision_sfx = pygame.mixer.Sound("Audio/collision_sfx (1)-[AudioTrimmer.com].mp3")
collision_sfx.set_volume(0.5)
scoring_sfx = pygame.mixer.Sound("Audio/scoring_sfx (1) (1)-[AudioTrimmer.com].mp3")
scoring_sfx.set_volume(0.5)

# Constants
WIDTH, HEIGHT = (800, 840)
GREY = (235, 235, 235)
CREAM = (249, 244, 235)
RED = (214, 73, 59)
HAND_CURSOR = pygame.SYSTEM_CURSOR_HAND
POINTER_CURSOR = pygame.SYSTEM_CURSOR_ARROW
TEXT_CURSOR = pygame.SYSTEM_CURSOR_IBEAM

# Flags & variables
run_title: bool = True
run_settings: bool = False
run_game: bool = False
run_end: bool = False
difficulty: int = 1
paddle_colour: int = 0
max_score: int = 10
first_run: bool = True
counter_x: int = 0
counter_y: int = 0
counter_edge: int = 0
counter_paddle: int = 0 
scorer: str = None

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

class Table:

    def __init__(self) -> None:

        image = pygame.image.load("interface_screens/table.png")
        height = image.get_height()

        scale = HEIGHT / height
        self.image = pygame.transform.scale_by(image, scale)

        self.height = self.image.get_height()
        self.width = self.image.get_width()

    def draw(self, screen) -> None:

        # Fill the background colour to cream
        screen.fill((249, 244, 235))

        # Display the table onto the screen
        screen.blit(self.image, (0,0))

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
        self.mask = pygame.mask.from_surface(self.image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity = np.array([0, 0])
        self.max_vel = np.array([800, 800])
        self.initial_pos = np.array([0,0])
        self.final_pos = np.array([0,0])

    # Procedure to move the paddle on the screen based on the user's mouse placement

    def move_paddle(self) -> None:

        mouse_pos = pygame.mouse.get_pos()

        # Convert to an array to make the position mutable
        draw_pos = np.array([mouse_pos[0], mouse_pos[1]])

        # Ensure that the paddle is drawn only in a valid position
        # n.b. /2 is for the radial length

        if mouse_pos[0] < (5 + int(self.width/2)):
            draw_pos[0] = 5 + self.width / 2 

        elif mouse_pos[0] > (TABLE_WIDTH - int(self.width / 2) - 5):
            draw_pos[0] = (TABLE_WIDTH - int(self.width / 2) - 5)

        if mouse_pos[1] < (TABLE_HEIGHT / 2 + int(self.width / 2)):
            draw_pos[1] = (TABLE_HEIGHT / 2 + int(self.width / 2))

        elif mouse_pos[1] > (TABLE_HEIGHT - int(self.width / 2)):
            draw_pos[1] = (TABLE_HEIGHT - int(self.width / 2))

        # Ensure that the rectangular hitbox of the paddle aligns with the position of the paddle image currently
        self.rect.center = tuple(draw_pos)
        pygame.draw.rect(screen, (0,0,0), self.rect, 1)

        screen.blit(self.image, (draw_pos[0]-self.width/2, draw_pos[1]-self.height/2))

    def determine_vel(self) -> None:

        # Calculate the time that a frame lasts (n.b. 60 fps)
        dt = 1 / 60

        # We will use vector properties to simplify and speed up calculations using numpy arrays

        # Calculate the change in the x and y positions and calculate the instantaneous velocity of the paddle
        dx_dy = self.final_pos - self.initial_pos

        self.velocity = dx_dy / dt

        # Ensure that the velocity is an integer number
        self.velocity = self.velocity.astype(int)

        self.initial_pos = self.final_pos
        self.final_pos = np.array(list(pygame.mouse.get_pos())) # Convert back into an array for calculations

    # def check_puck_collision(self, Puck: object) -> bool:

    #     # First check whether the rectangular area of the puck and paddle images overlap
    #     if self.rect.colliderect(Puck.rect) == False:

    #         return False
        
    #     else:

    #         offset_x = Puck.rect.left - self.rect.left
    #         offset_y = Puck.rect.top - self.rect.top

    #         # If their rectangle areas overlap, check if their images actually overlap
    #         if self.mask.overlap(Puck.mask, (offset_x, offset_y)):

    #             return True
            
    #         return False

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


class Puck:

    def __init__(self, image_file: str, scale: float) -> None:

        image = pygame.image.load(image_file)
        self.image = pygame.transform.scale_by(image, scale)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.position = np.array([282, 413]).astype(int)
        self.height = self.image.get_height()
        self.width = self.image.get_width()

        self.rect.center = tuple(self.position)

        self.velocity = np.array([0,0]).astype(int)
        self.deceleration = 0.9999

    # Subroutine to reset the table after a goal has been scored

    def reset(self):

        self.position = np.array([282, 413]).astype(int)
        self.velocity = np.array([0,0]).astype(int)

    # Subroutine for testing, allowing me to move the puck with my cursor

    def test_puck(self) -> None:

        mouse_pos = pygame.mouse.get_pos()

        # Ensure that the rectangular hitbox of the puck aligns with the position of the puck image currently
        self.rect.center = tuple(mouse_pos)
        pygame.draw.rect(screen, (0,0,0), self.rect, 1)

        screen.blit(self.image, (mouse_pos[0]-self.width/2, mouse_pos[1]-self.height/2))

    # Subroutine to update the position of the puck and move it accordingly

    def update_pos(self) -> None:

        # Calculate the distance that the puck should move in the time the frame lasts
        dt = 1 / 60
        self.position = self.position + dt * self.velocity
        self.position = self.position.astype(int)
        self.rect.center = tuple(self.position)

        screen.blit(self.image, (self.position[0] - int(self.width / 2), self.position[1] - int(self.height / 2)))

    def check_wall_collision(self, Computer_Goal: object, Player_Goal: object) -> tuple:

        x_collision: bool = False
        y_collision: bool = False
        goal_collision: bool = False
        collision_centre: tuple = (0,0)
        goal_to_check: object = None

        # Check whether the puck exceeds the area of the table
        if self.rect.left <= 9 or self.rect.right >= (TABLE_WIDTH - 9):
            x_collision = True

        if self.rect.top <= 9 or self.rect.bottom >= (TABLE_HEIGHT - 9):

            comp_collided = self.rect.colliderect(Computer_Goal.rect)
            p_collided = self.rect.colliderect(Player_Goal.rect)

            # If one of the goals is collided with, check for goal collisions
            if comp_collided or p_collided:

                if comp_collided:

                    Goal = Computer_Goal

                elif p_collided:

                    Goal = Player_Goal

                # We will check whether the distance to the corner of the goal is <= radius to check for collision inside the goal
                distance_left = sqrt( (Goal.left_corner[0] - self.rect.center[0])**2 + (Goal.left_corner[1] - self.rect.center[1])**2 ) 
                distance_right = sqrt( (Goal.right_corner[0] - self.rect.center[0])**2 + (Goal.right_corner[1] - self.rect.center[1])**2 )

                # To ensure a correct collision, ensure that the puck approaches from the correct side to register a collision
                if distance_left <= (self.width / 2) + 1 and self.velocity[0] <= 0:

                    goal_collision = True
                    collision_centre = Goal.left_corner

                elif distance_right <= (self.width / 2) + 1 and self.velocity[0] >= 0:

                    goal_collision = True
                    collision_centre = Goal.right_corner

                else:

                    # If this is triggered, we need to ensure that a goal has actually been scored
                    goal_to_check = Goal

            else:

                y_collision = True

        return x_collision, y_collision, goal_collision, collision_centre, goal_to_check


    # Subroutine to update the velocity of the puck based on its interactions on the table 

    def update_velocity(self, Paddle: object, paddle_collision: bool, x_collision: bool, y_collsion: bool, 
                        goal_collision: bool, collision_centre) -> None:

        if paddle_collision == True:

            # Determine the normal to the paddle to reflect the puck off of
            normal = np.array(self.rect.center) - np.array(Paddle.rect.center)
            magnitude = np.linalg.norm(normal)

            # Find the unit vector of the normal line
            unit_normal = normal / magnitude

            # Calculate the new velocity of the puck
            self.velocity = self.velocity - 2 * np.dot(self.velocity-Paddle.velocity, unit_normal) * unit_normal
            self.velocity = self.velocity.astype(int)

            collision_sfx.play()

        if goal_collision == True:

            # Reflect the puck correctly off of the corner of the goal
            normal = np.array(self.rect.center) - collision_centre
            magnitude = np.linalg.norm(normal)

            # Find unit vector of the normal line
            unit_normal = normal / magnitude
            
            # Reflect the puck's movement
            self.velocity = self.velocity - 2 * np.dot(self.velocity, unit_normal) * unit_normal
            self.velocity = self.velocity.astype(int)

            collision_sfx.play()

        if x_collision == True:

            self.velocity[0] = int(-self.velocity[0] * 0.9)
            collision_sfx.play()

        if y_collision == True:

            self.velocity[1] = int(-self.velocity[1] * 0.9)
            collision_sfx.play()

        # Decellerate the puck due to friction

        self.velocity = self.velocity * self.deceleration
        self.velocity = self.velocity.astype(int)

        

# Class for the scoreboard

class Scoreboard:

    def __init__(self, p_position: tuple, comp_position: tuple, font_file:  str, font_size: int) -> None:

        self.font = pygame.font.Font(font_file, font_size)

        self.p_score: int = 0
        self.comp_score: int = 0

        # The position where the score should be displayed
        self.p_position: tuple = p_position
        self.comp_position: tuple = comp_position

        self.multiplier = 1

    def draw(self) -> None:

        p_score_display = self.font.render(str(self.p_score), True, RED, None)
        p_score__rect = p_score_display.get_rect()
        p_score__rect.center = self.p_position

        comp_score_display = self.font.render(str(self.comp_score), True, RED, None)
        comp_score__rect = comp_score_display.get_rect()
        comp_score__rect.center = self.comp_position

        screen.blit(p_score_display, ((self.p_position[0] - p_score__rect.width/2), (self.p_position[1] - p_score__rect.height/2)))
        screen.blit(comp_score_display, ((self.comp_position[0] - comp_score__rect.width/2), (self.comp_position[1] - comp_score__rect.height/2)))

    def update_score(self, player: str):

        if player == "computer":

            self.comp_score += self.multiplier

        elif player == "player":

            self.p_score += self.multiplier
        
class Goal:

    def __init__(self, x: int, y: int, player: str) -> None:

        self.width = 150
        self.x = x
        self.y = y
        self.player = player

        self.rect = pygame.Rect(self.x, self.y, self.width, 100)
        self.mask = pygame.mask.Mask((self.rect.width, self.rect.height), True)

        if self.player == "computer":

            self.left_corner = (self.rect.left, self.rect.bottom)
            self.right_corner = (self.rect.right, self.rect.bottom)

        elif self.player == "player":

            self.left_corner = (self.rect.left, self.rect.top)
            self.right_corner = (self.rect.right, self.rect.top)
        

    def draw(self) -> None:

        pygame.draw.rect(screen, (0,0,0), self.rect)

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

Scoreboard_Display = Scoreboard(p_position=(680,210), comp_position=(680,630), font_file="Fonts/Grand9K Pixel.ttf", font_size=100)

Table_Display = Table()

Puck_Display = Puck(image_file="red_puck.png", scale=0.4)

TABLE_HEIGHT = Table_Display.height
TABLE_WIDTH = Table_Display.width

Comp_Goal = Goal(206, -90, "computer")
Player_Goal = Goal(206, 830, "player")
 


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


            Table_Display.draw(screen)
            Scoreboard_Display.draw()
            Puck_Display.update_pos()
            # Puck_Display.test_puck()

            if scorer:

                scoring_sfx.play()
                Scoreboard_Display.update_score(scorer)
                Puck_Display.reset()
                scorer = None
                sleep(1)
                continue
        
            # If the first run, instantiate the paddle, preventing reinstantiation every loop
            if first_run:

                paddle_image = Paddles[paddle_colour].image
                User_Paddle = Paddle(paddle_image)
                first_run = False

            User_Paddle.move_paddle()
            User_Paddle.determine_vel()

            paddle_collision = User_Paddle.check_puck_collision(Puck_Display)

            if paddle_collision == True:

                counter_paddle += 1
                
                if counter_paddle > 1:

                    paddle_collision = False

            else:

                counter_paddle = 0

            x_collision, y_collision, goal_collision, collision_centre, goal_to_check = Puck_Display.check_wall_collision(Comp_Goal, Player_Goal)

            # print(x_collision, y_collision, goal_collision, collision_centre)

            # To prevent registering a wall collision multiple times before the puck has actually moved off of the wall

            if x_collision == True:

                counter_x += 1
                
                if counter_x > 1:

                    x_collision = False

            else:

                counter_x = 0

            if y_collision == True:

                counter_y += 1
                
                if counter_y > 1:

                    y_collision = False

            else:

                counter_y = 0

            if goal_collision == True:

                counter_edge += 1
                
                if counter_edge > 1:

                    goal_collision = False

            else:

                counter_edge = 0

            Puck_Display.update_velocity(User_Paddle, paddle_collision, x_collision, y_collision, goal_collision, collision_centre)

            Comp_Goal.draw()
            Player_Goal.draw()

            if goal_to_check:

                scorer = goal_to_check.check_goal(Puck_Display)
                

            # Check whether a goal in this frame

            # scorer = Comp_Goal.check_goal(Puck_Display)

            # if scorer != None:

            #     print(scorer)



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

