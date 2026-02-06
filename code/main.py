# Libraries
import pygame
import numpy as np
from sys import exit
from math import sqrt, inf
from time import sleep, time
from random import randint, choice

# Importing my python classes
from heap_classes import Heap
import goal_classes
import puck_classes
import paddle_classes
import power_up_classes
import computer_classes

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
BLACK = (0,0,0)
LIGHT_GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)
BRIGHT_RED = (255, 0, 0)

GLOWS = {"red": (255, 0, 0, 50),
         "blue": (38, 247, 253, 50),
         "green": (45, 254, 84, 50),
         "purple": (191, 64, 191, 50)}

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
first_collection: bool = True
start_time: float = None
end_time: float = None
spawn_power_ups: bool = False
start_clock: bool = True
first_spawn: bool = True
delay_start: float = None
delay_end: float = None
delay_elapsed: float = 0.0
trigger_delay: bool = True
counter: int = 0
computer_counter: int = 0 

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

    def __init__(self, image, colour: str) -> None:

        self.image = image
        self.colour = colour
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity = np.array([0, 0])
        self.initial_pos = np.array([0,0])
        self.final_pos = np.array([0,0])

        # Flag to disable movement if frozen:
        self.frozen = False

        # Flag to check if the power shot power up is active
        self.power_shot = False
        self.position_reset = False

    # Procedure to move the paddle on the screen based on the user's mouse placement

    def move_paddle(self) -> None:

        # If the paddle is frozen, fix the paddle to its most recent position
        if self.frozen:

            draw_pos = self.final_pos
            self.velocity = np.array([0, 0])

        elif not self.frozen:

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
            self.velocity = np.round(self.velocity, decimals=0)

            if self.power_shot == True:

                self.velocity = self.velocity * 2

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
        self.glow_colour = (0, 0, 0, 0)
        
        self.mask = pygame.mask.from_surface(self.image)

        self.position = np.array([282, 413]).astype(int)
        self.previous_pos = np.array([282, 413]).astype(int)
        self.height = self.image.get_height()
        self.width = self.image.get_width()

        self.rect.center = tuple(self.position)

        self.velocity = np.array([0,0]).astype(int)
        self.max_vel = 3000
        self.deceleration = 0.9999

        self.test = False
        self.top_left_valid = ( 5 + int(self.width / 2) , 5 + int(self.width / 2) )
        self.bottom_right_valid = ( TABLE_WIDTH - int(self.width / 2) - 5, TABLE_HEIGHT - int(self.width / 2) - 5 )


        # Flag to check for testing

    def check_stuck(self, Computer_Goal: object, Player_Goal: object) -> tuple:

        left_stuck = False
        right_stuck = False
        top_stuck = False
        bottom_stuck = False

        # If the puck is stuck on the wall of the table without moving off it, return that the puck is stuck

        if not self.rect.colliderect(Computer_Goal.rect) and not self.rect.colliderect(Player_Goal.rect):

            if self.position[0] == self.top_left_valid[0] and self.velocity[0] <= 0:

                left_stuck = True

            elif self.position[0] == self.bottom_right_valid[0] and self.velocity[0] >= 0: 

                right_stuck = True

            if self.position[1] == self.top_left_valid[1] and self.velocity[1] <= 0:

                top_stuck = True

            elif self.position[1] == self.bottom_right_valid[1] and self.velocity[1] >= 0: 

                bottom_stuck = True

        return left_stuck, right_stuck, top_stuck, bottom_stuck


    # Subroutine to reset the table after a goal has been scored

    def reset(self):

        self.position = np.array([282, 413]).astype(int)
        self.velocity = np.array([0,0]).astype(int)

    # Subroutine for testing, allowing me to move the puck with my cursor

    def test_puck(self) -> None:

        mouse_pos = pygame.mouse.get_pos()

        # Ensure that the rectangular hitbox of the puck aligns with the position of the puck image currently
        self.rect.center = mouse_pos
        self.position = mouse_pos
        pygame.draw.rect(screen, (0,0,0), self.rect, 1)

        screen.blit(self.image, (mouse_pos[0]-self.width/2, mouse_pos[1]-self.height/2))

    # Subroutine to update the position of the puck and move it accordingly

    def update_pos(self, Computer_Goal: object, Player_Goal: object, temp_velocity: np.ndarray = None, temp_position: np.ndarray = None) -> np.ndarray:

        # Check if a velocity is passed so that we can reuse this function for predicting position
        if temp_velocity is None:

            puck_velocity = self.velocity
            position = self.position

        else:

            puck_velocity = temp_velocity
            position = temp_position
    

        # Calculate the distance that the puck should move in the time the frame lasts
        dt = 1 / 60
        position = position + dt * puck_velocity
        # print(f"Unrounded position is {position}")
        position = np.round(position, decimals=0)

        if temp_velocity is None:

            self.position = position

            # Display the glow to identify who the shot stopper power up is active for IF ACTIVE
            glow_surface = self.mask.to_surface(setcolor=self.glow_colour, unsetcolor=None)
            glow_surface = pygame.transform.scale_by(glow_surface, 1.3)

            # Check if the puck is within the bounds of the table as long as it is not entering the goal 

            if not self.rect.colliderect(Computer_Goal.rect) and not self.rect.colliderect(Player_Goal.rect):

                if self.position[0] < self.top_left_valid[0]:

                    self.position[0] = self.top_left_valid[0]

                elif self.position[0] > self.bottom_right_valid[0]:

                    self.position[0] = self.bottom_right_valid[0]

                if self.position[1] < self.top_left_valid[1]:

                    self.position[1] = self.top_left_valid[1]

                elif self.position[1] > self.bottom_right_valid[1]:

                    self.position[1] = self.bottom_right_valid[1]


            self.rect.center = tuple(self.position)
            # pygame.draw.rect(screen, (0,0,0), self.rect, 1)

            screen.blit(glow_surface, (self.position[0] - int(glow_surface.get_width() / 2), self.position[1] - int(glow_surface.get_height() / 2)))
            screen.blit(self.image, (self.position[0] - int(self.width / 2), self.position[1] - int(self.height / 2)))

            # self.rect.center = tuple(self.position)

        return position

    

    def check_wall_collision(self, Computer_Goal: object, Player_Goal: object, temp_position: np.ndarray = None) -> tuple:

        x_collision: bool = False
        y_collision: bool = False
        goal_collision: bool = False
        collision_centre: tuple = (0,0)
        goal_to_check: object = None

        # Check if a position is passed so that we can reuse this function for predicting position

        if temp_position is None:

            puck_position = self.position
            temp_rect = self.rect

        else:

            puck_position = temp_position
            temp_rect = self.image.get_rect()

        temp_rect.center = puck_position

        # Check whether the puck exceeds the area of the table
        if temp_rect.left <= 9 or temp_rect.right >= (TABLE_WIDTH - 9):
            x_collision = True

        if temp_rect.top <= 9 or temp_rect.bottom >= (TABLE_HEIGHT - 9):

            comp_collided = temp_rect.colliderect(Computer_Goal.rect)
            p_collided = temp_rect.colliderect(Player_Goal.rect)

            # If the goal is suspended due to the shot stopper power up, do not consider the hitbox of the suspended goal
            if Computer_Goal.display == False:

                comp_collided = False

            elif Player_Goal.display == False:

                p_collided = False

            # If one of the goals is collided with, check for goal collisions
            if comp_collided or p_collided:

                if comp_collided:

                    Goal = Computer_Goal

                elif p_collided:

                    Goal = Player_Goal

                # We will check whether the distance to the corner of the goal is <= radius to check for collision inside the goal
                distance_left = sqrt( (Goal.left_corner[0] - temp_rect.center[0])**2 + (Goal.left_corner[1] - temp_rect.center[1])**2 ) 
                distance_right = sqrt( (Goal.right_corner[0] - temp_rect.center[0])**2 + (Goal.right_corner[1] - temp_rect.center[1])**2 )

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

    def update_velocity(self, Paddle: object, paddle_collision: bool, x_collision: bool, y_collision: bool, 
                        goal_collision: bool, collision_centre: np.ndarray, Player_Goal: object, Computer_Goal: object,
                        temp_velocity: np.ndarray = None) -> np.ndarray:

        # So that we can extend this function to predict the position of the puck, we will have an optional parameter to base the velocity off of

        if temp_velocity is None:

            puck_velocity = self.velocity

        else:

            puck_velocity = temp_velocity
            
        if paddle_collision == True:

            # Determine the normal to the paddle to reflect the puck off of
            normal = np.array(self.rect.center) - np.array(Paddle.rect.center)
            magnitude = np.linalg.norm(normal)

            # Find the unit vector of the normal line
            unit_normal = normal / magnitude

            # Calculate the new velocity of the puck
            puck_velocity = puck_velocity - 2 * np.dot(puck_velocity-Paddle.velocity, unit_normal) * unit_normal
            puck_velocity = np.round(puck_velocity, decimals=0)

        if goal_collision == True:

            # Reflect the puck correctly off of the corner of the goal
            normal = np.array(self.rect.center) - collision_centre
            magnitude = np.linalg.norm(normal)

            # Find unit vector of the normal line
            unit_normal = normal / magnitude
            
            # Reflect the puck's movement
            puck_velocity = puck_velocity - 2 * np.dot(puck_velocity, unit_normal) * unit_normal
            puck_velocity = np.round(puck_velocity, decimals=0)

        if x_collision == True:

            puck_velocity[0] = int(-puck_velocity[0] * 0.9)

        if y_collision == True:

            puck_velocity[1] = int(-puck_velocity[1] * 0.9)

        # Decellerate the puck due to friction

        puck_velocity = puck_velocity * self.deceleration
        puck_velocity = np.round(puck_velocity, decimals=0)

        left_stuck, right_stuck, top_stuck, bottom_stuck = self.check_stuck(Computer_Goal=Computer_Goal, Player_Goal=Player_Goal)

        if left_stuck:

            puck_velocity[0] = 50

        if right_stuck:

            puck_velocity[0] = -50

        if top_stuck:

            puck_velocity[1] = 50

        if bottom_stuck:

            puck_velocity[1] = -50

        # To prevent the puck from moving too fast, cap its velocity
        vel_magnitude = np.linalg.norm(puck_velocity)

        if vel_magnitude > self.max_vel:
            
            puck_velocity = puck_velocity / vel_magnitude * self.max_vel
            puck_velocity = np.round(puck_velocity, decimals=0)

        if self.test:

            puck_velocity = np.array([0,0])

        # If the velocity was not given, update the actual velocity of the puck
        if temp_velocity is None:

            self.velocity = puck_velocity


        return puck_velocity
    
    # Subroutine to predict the position of the puck a few frames ahead

    def predict_pos(self, Computer_Goal: object, Player_Goal: object) -> np.ndarray:

        # We want to calculate the distance travelled per frame - at 60 fps, this means a frame runs for 1/60 of a second
        dt = 1 / 60

        # Flags for keeping track of whether collisions have already been registered and accounted for

        counter_x = 0
        counter_y = 0
        counter_edge = 0

        # As we only want to predict the position, we will hold velocity and position temporarily as to not move the actual puck
        current_velocity = self.velocity.copy()
        new_position = self.position.copy()

        # We will be predicting 5 frames ahead to give the computer some "reaction time" to the movement of the puck
        for i in range(5):

            # Check if there are any collisions in this new position to correctly predict the velocity and future puck position
            x_collision, y_collision, goal_collision, collision_centre, goal_to_check = self.check_wall_collision(Computer_Goal=Computer_Goal, 
                                                                                                                  Player_Goal=Player_Goal, 
                                                                                                                  temp_position=new_position)
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
            
            current_velocity = self.update_velocity(Paddle=None, paddle_collision=False, x_collision=x_collision, 
                                                    y_collision=y_collision, goal_collision=goal_collision, collision_centre=collision_centre,
                                                    Computer_Goal=Computer_Goal, Player_Goal=Player_Goal, temp_velocity=current_velocity)
            
            new_position = self.update_pos(Computer_Goal=Computer_Goal, Player_Goal=Player_Goal, temp_velocity=current_velocity, temp_position=new_position)

        return new_position

        

# Class for the scoreboard

class Scoreboard:

    def __init__(self, p_position: tuple, comp_position: tuple, font_file:  str, font_size: int) -> None:

        self.font = pygame.font.Font(font_file, font_size)

        self.p_score: int = 0
        self.comp_score: int = 0

        # The position where the score should be displayed
        self.p_position: tuple = p_position
        self.comp_position: tuple = comp_position

        self.p_multiplier = 1
        self.comp_multiplier = 1

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

            self.comp_score += self.comp_multiplier

        elif player == "player":

            self.p_score += self.p_multiplier
        
class Goal:

    def __init__(self, x: int, y: int, player: str) -> None:

        self.width = 150
        self.x = x
        self.y = y
        self.player = player

        self.rect = pygame.Rect(self.x - self.width / 2, self.y, self.width, 100)
        self.mask = pygame.mask.Mask((self.rect.width, self.rect.height), True)

        # Flag to check whether the goal is open
        self.display = True

        if self.player == "computer":

            self.left_corner = (self.rect.left, self.rect.bottom)
            self.right_corner = (self.rect.right, self.rect.bottom)

        elif self.player == "player":

            self.left_corner = (self.rect.left, self.rect.top)
            self.right_corner = (self.rect.right, self.rect.top)
        

    def draw(self) -> None:

        if self.display:

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
            
class GridSquare:

    def __init__(self, position: tuple):

        self.is_obstacle: bool = False
        self.is_target: bool = False
        self.is_start: bool = False
        self.is_discovered: bool = False
        self.weight: int = 0

        self.colour = BLACK

        # We will initially set all undiscovered nodes to have infinite weight
        self.f_cost: float = inf
        self.g_cost: float = inf
        self.h_cost: float = inf

        self.pointer = np.array([None, None])
        self.neighbours = []

        # Each grid square will be 5x5 pixels in dimension
        self.rect = pygame.Rect(position[0] * 5, position[1] * 5, 5, 5)

    def draw(self) -> None:

        if not self.is_obstacle and not self.is_start and not self.is_discovered and not self.is_target:

            pygame.draw.rect(screen, self.colour, self.rect, 1)
        
        else:

            if self.is_obstacle:
                self.colour = BLACK

            elif self.is_target:
                self.colour = LIGHT_GREEN

            elif self.is_start:
                self.colour = BRIGHT_RED
            
            elif self.is_discovered:
                self.colour = ORANGE


            pygame.draw.rect(screen, self.colour, self.rect)




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
        self.rect = pygame.Rect(0, 0, 30, 30)

        self.x = None
        self.y = None

        self.test = False

    # Randomise the power up to be given and its spawn position
    def randomise_spawn(self) -> None:

        if self.test:

            self.power_up = "power_shot"

        elif not self.test:

            # Choose a random power up from the selection:
            self.power_up = choice(self.power_ups)

        # Load the corresponding image and scale accordingly
        image = pygame.image.load(self.images[self.power_up])
        self.image = pygame.transform.scale(image, (30, 30))

        # Randomly generate coordinates to spawn the power up in, accouting for the power up dimensions and walls of the table
        self.x = randint(int(self.half_dimensions[0] + 10 + 15), int(self.half_dimensions[1] - 10 - 15))
        self.y = randint(int(self.half_dimensions[2] + 10 + 15), int(self.half_dimensions[3] - 15))

        # Reposition the hitbox of the power up and display the power up on the screen
        self.rect.center = (self.x, self.y)

    # Draw the power up on the screen
    def draw(self) -> None:

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
            Goal.rect = pygame.Rect(Goal.x - Goal.width / 2, Goal.y, Goal.width, 100)
            Goal.mask = pygame.mask.Mask((Goal.rect.width, Goal.rect.height), True)
            
            if Goal.player == "computer":

                Goal.left_corner = (Goal.rect.left, Goal.rect.bottom)
                Goal.right_corner = (Goal.rect.right, Goal.rect.bottom)

            elif Goal.player == "player":

                Goal.left_corner = (Goal.rect.left, Goal.rect.top)
                Goal.right_corner = (Goal.rect.right, Goal.rect.top)

        # If this power up is not active, then reset the goal's hitbox
        if not self.is_active:

            Goal.width = 150
            Goal.rect = pygame.Rect(Goal.x - Goal.width / 2, Goal.y, Goal.width, 100)
            Goal.mask = pygame.mask.Mask((Goal.rect.width, Goal.rect.height), True)
            
            if Goal.player == "computer":

                Goal.left_corner = (Goal.rect.left, Goal.rect.bottom)
                Goal.right_corner = (Goal.rect.right, Goal.rect.bottom)

            elif Goal.player == "player":

                Goal.left_corner = (Goal.rect.left, Goal.rect.top)
                Goal.right_corner = (Goal.rect.right, Goal.rect.top)

    def enlarge_paddle(self, Paddle: object, optional=None) -> None:

        # If the power up is active, enlarge the hitbox of the paddle
        if self.is_active:

            Paddle.image = pygame.transform.scale2x(Paddle.image)
            Paddle.width = Paddle.image.get_width()
            Paddle.height = Paddle.image.get_height()

        # Otherwise, rescale the paddle's hitbox to what it was originally
        if not self.is_active:

            Paddle.image = pygame.transform.scale_by(Paddle.image, 0.5)
            Paddle.width = Paddle.image.get_width()
            Paddle.height = Paddle.image.get_height()

    def shot_stopper(self, Paddle: object, Puck: object, Goal: object, Scoreboard: object) -> None:

        if self.is_active:

            Puck.glow_colour = GLOWS[Paddle.colour]
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

# We will create the classes for the computer's gameplay

class Computer_Easy:

    def __init__(self, image_file: str):

        image = pygame.image.load(image_file)
        self.image = pygame.transform.scale_by(image, 0.5)
    
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_magnitude = 100
        self.velocity = np.array([0,0])
        self.position = np.array([282, 150])

        self.colour = "blue"

        # Flag to disable movement if frozen:
        self.frozen = False

        # Flag to check if the power shot power up is active
        self.power_shot = False

    # The puck collision method will remain the same as the Paddle class

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
    
    # Subroutine to move the computer paddle
    def move_paddle(self, Puck: object, Computer_Goal: object, Player_Goal: object) -> None:

        # If frozen, prevent the paddle from moving

        if self.frozen:

            self.velocity = np.array([0,0])

        elif not self.frozen:

            # Time a frame lasts to calculate the maximum distance the computer can travel in a frame
            dt = 1 / 60
            self.vel_magnitude = 500
            avoid = False   # Flag to determine whether the puck is likely to get trapped

            # Work out the direction needed to move the paddle in to meet the puck
            predicted_pos = Puck.predict_pos(Computer_Goal, Player_Goal)


            # If the puck is going to be cornered, force the computer to move away from the puck, adding a buffer to give the paddle time to move out the way

            if (Puck.position[0] <= Puck.top_left_valid[0] + 10 or Puck.position[0] >= Puck.bottom_right_valid[0] - 10 
                or Puck.position[1] <= Puck.top_left_valid[1] + 10):

                avoid = True
                predicted_pos = np.array([282,150])
            
            # Calculate the velocity the computer needs to travel at to move towards the puck
            direction_vector = predicted_pos - self.position
            direction_magnitude = np.linalg.norm(direction_vector)
            self.velocity = (self.vel_magnitude / direction_magnitude) * direction_vector
            self.velocity = np.round(self.velocity, decimals=0)

            # Update the position of the paddle
            
            # Save previous conditions and attributes to reset if problematic movement is detected
            previous_puck_collision = self.check_puck_collision(Puck)
            previous_position = self.position.copy()

            self.position = self.position + self.velocity * dt
            self.position = np.round(self.position, decimals=0)
            self.rect.center = tuple(self.position)

            # Check if the new position forces repeated collision with the puck which could cause the puck to get stuck
            new_puck_collision = self.check_puck_collision(Puck)

            # If the new position continues to register a collision, reset position so that it avoids problematic interactions
            if new_puck_collision and previous_puck_collision and avoid == False:

                self.position = previous_position
                self.rect.center = tuple(self.position)

            else:

                if self.position[0] < (5 + int(self.width/2)):
                    self.position[0] = 5 + int(self.width / 2) 

                elif self.position[0] > (TABLE_WIDTH - int(self.width / 2) - 5):
                    self.position[0] = (TABLE_WIDTH - int(self.width / 2) - 5)

                if self.position[1] < (5 + int(self.width/2)):
                    self.position[1] = (5 + int(self.width/2))

                elif self.position[1] > (TABLE_HEIGHT / 2 - int(self.width / 2)):
                    self.position[1] = (TABLE_HEIGHT / 2 - int(self.width / 2))

            

    def reset(self) -> None:

        self.position = np.array([282, 150])
        self.velocity = np.array([0,0])

    def draw(self, Puck: object) -> None:

        screen.blit(self.image, (self.position[0]-self.width/2, self.position[1]-self.height/2))

    def hold_position(self, Puck: object) -> None:

        if not self.frozen:

            dt = 1 / 60

            distance_y = 0
            self.vel_magnitude = 200

            # Track the x-coordinate of the puck to anticipate its movement
            distance_x = Puck.position[0] - self.position[0]
            self.velocity[0] = distance_x / dt

            # while the puck is not in the computer half, make it back to the centre line to anticipate the puck's movement
            if self.position[1] != 150:

                self.vel_magnitude = 500
                distance_y = 150 - self.position[1]
                self.velocity[1] = distance_y / dt

            vel_magnitude = np.linalg.norm(self.velocity)

            if vel_magnitude == 0:

                self.velocity = np.array([0,0])

            else:

                self.velocity = self.velocity / vel_magnitude * self.vel_magnitude
                self.velocity = np.round(self.velocity, decimals=0)

            # Update the velocity accordingly
            self.position = self.position + self.velocity * dt
            self.position = np.round(self.position, decimals=0)

            # Check the direction the paddle is moving back to the centre position

            if distance_y <= 0:

                if self.position[1] <= 150:

                    self.position[1] = 150

            if distance_y >= 0:

                if self.position[1] >= 150:
                    
                    self.position[1] = 150

            self.rect.center = tuple(self.position)

# To create the medium difficulty bot, I will be inheriting from the Computer_Easy Class

class Computer_Medium(Computer_Easy):

    def __init__(self, image_file: str) -> None:

        super().__init__(image_file)

    def find_path(self, start_node: object, target_node: object):

        # Open list - these are the nodes yet to be explored
        # This will use a min heap priority queue to efficiently explore the next node with minimum f cost
        open = Heap(np.full(100, None))

        # Closed list for already discovered nodes
        closed = []

        current_node = start_node

        while current_node is not None:

            if target_node in current_node.neighbours:

                target_node.pointer = current_node
                current_node = None
                continue

            else:

                for neighbour in current_node.neighbours:

                    # Ignore any obstacle squares - we cannot traverse these
                    if neighbour.is_obstacle == True:

                        continue

                    else:

                        # The g_cost will also include a weight, indicating whether this square is a preferred route
                        g_cost = current_node.g_cost + neighbour.weight + (neighbour.centre - current_node.rect.centre)

                        # As the h_cost is constant, instead of comparing f_costs, we can just compare g_costs of the previous and current paths
                        # If the g_cost of the current path is lower, a better path to this square has been found
                        if g_cost < neighbour.g_cost:

                            neighbour.g_cost = g_cost
                            neighbour.h_cost = np.linalg.norm(target_node.centre - current_node.centre)
                            neighbour.f_cost = neighbour.g_cost + neighbour.h_cost

                            # Now we have found a better path, redirect the pointer of the neighbour to the current node
                            neighbour.ponter = current_node

                            # If the neighbour has not yet been "discovered", add it to open with its costs evaluated
                            if neighbour not in closed and neighbour not in open.heap:
                            
                                open.insert(neighbour)

                            # If the node has already been explored, reopen the node - this will be useful for GAA*
                            elif neighbour in closed:

                                closed.remove(neighbour)
                                open.insert(neighbour)

                current_node = open.extract()

        # Now that we have gotten to the target node, backtrack to find the completed path

                            










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

Paddles = [(Red_Paddle_Icon, "red"), (Blue_Paddle_Icon, "blue"), (Green_Paddle_Icon, "green"), (Purple_Paddle_Icon, "purple")]
Difficulties = [[Easy_Icon, Easy_Letters], [Medium_Icon, Medium_Letters], [Hard_Icon, Hard_Letters]]

Scoreboard_Display = Scoreboard(p_position=(680,210), comp_position=(680,630), font_file="Fonts/Grand9K Pixel.ttf", font_size=100)

Table_Display = Table()

TABLE_HEIGHT = Table_Display.height
TABLE_WIDTH = Table_Display.width

Puck_Display = Puck(image_file="red_puck.png", scale=0.4)

Comp_Goal = Goal(281, -90, "computer")
Player_Goal = Goal(281, 830, "player")

PlayerPowerUp = PowerUp((0, TABLE_WIDTH, TABLE_HEIGHT / 2, TABLE_HEIGHT), player="player")
CompPowerUp = PowerUp((0, TABLE_WIDTH, 0, TABLE_HEIGHT / 2), player="computer")


# Setting up the grid for pathfinding 

def create_grid(Paddle: object) -> list:
    
    grid = []
    
    half_height = TABLE_HEIGHT / 2

    # We will use grids that are 10x10 pixels in dimension

    columns = int(half_height / 5)
    rows = int((TABLE_WIDTH - 2) / 5)    # n.b -2 because the actual widht is 567 which would lead to a float

    for row_number in range(rows):
        
        row = []

        for column_number in range(columns):

            row.append(GridSquare((row_number, column_number)))

            # Account for the collision space of the paddle and the walls to prevent computer traversal out of bounds
            
            if (row_number * 5) <= (10 + Paddle.width / 2) or (row_number * 5) >= (TABLE_WIDTH - Paddle.width / 2): 

                row[column_number].is_obstacle = True

            if (column_number * 5) <= (10 + Paddle.width / 2) or (column_number * 5) >= (TABLE_HEIGHT / 2 - 10 - Paddle.width / 2):

                row[column_number].is_obstacle = True

        grid.append(row)

    return grid




 


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

            Paddles[paddle_colour][0].draw()

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
            

            # If the first run, instantiate the paddle and grid, preventing reinstantiation every loop
            if first_run:

                paddle_image = Paddles[paddle_colour][0].image
                User_Paddle = Paddle(paddle_image, Paddles[paddle_colour][1])
                Computer_Paddle = Computer_Easy("icons/blue_paddle.png")
                first_run = False
                grid = create_grid(User_Paddle)

                user_power_ups = {"freeze": [PlayerPowerUp.freeze, (Computer_Paddle, None)],
                                  "double_points": [PlayerPowerUp.double_points, (Scoreboard_Display, None)],
                                  "widen_goal": [PlayerPowerUp.widen_goal, (Comp_Goal, None)],
                                  "enlarge_paddle": [PlayerPowerUp.enlarge_paddle, (User_Paddle, None)],
                                  "shot_stopper": [PlayerPowerUp.shot_stopper, (User_Paddle, Puck_Display, Player_Goal, Scoreboard_Display)],
                                  "power_shot": [PlayerPowerUp.power_shot, (User_Paddle, None)]}
                
                comp_power_ups = {"freeze": [CompPowerUp.freeze, (User_Paddle, None)],
                                  "double_points": [CompPowerUp.double_points, (Scoreboard_Display, None)],
                                  "widen_goal": [CompPowerUp.widen_goal, (Player_Goal, None)],
                                  "enlarge_paddle": [CompPowerUp.enlarge_paddle, (Computer_Paddle, None)],
                                  "shot_stopper": [CompPowerUp.shot_stopper, (Computer_Paddle, Puck_Display, Comp_Goal, Scoreboard_Display)],
                                  "power_shot": [CompPowerUp.power_shot, (Computer_Paddle, None)]}
                
            Table_Display.draw(screen)
            Scoreboard_Display.draw()
            Comp_Goal.draw()
            Player_Goal.draw()

            # If we are not in the stage of spawning power ups, wait for 10 seconds until the next power up spawn

            if not spawn_power_ups:

                if start_clock:

                    start_time = time()
                    start_clock = False

                else:

                    end_time = time()
                    elapsed = end_time - start_time

                    if elapsed >= 10:

                        spawn_power_ups = True
                        start_clock = True

            elif spawn_power_ups:

                if first_spawn == True:

                    PlayerPowerUp.randomise_spawn()
                    CompPowerUp.randomise_spawn()
                    first_spawn = False

                # Only check for collection of the power up if the power up has not yet been collected
                if not PlayerPowerUp.is_active and not CompPowerUp.is_active:
                    PlayerPowerUp.draw()
                    CompPowerUp.draw()
                    PlayerPowerUp.collect(User_Paddle)
                    CompPowerUp.collect(Computer_Paddle)

                if PlayerPowerUp.is_active:

                    # Retrieve the method and arguments
                    power_up_call = user_power_ups[PlayerPowerUp.power_up]

                    # If the power_up is just collected, start the timer
                    if first_collection:

                        first_collection = False
                        start_time = time()

                        # Call the method using the predetermined arguments
                        power_up_call[0](*power_up_call[1])

                    else:

                        end_time = time()
                        elapsed = end_time - start_time

                        if elapsed >= 5:

                            first_collection = True
                            PlayerPowerUp.is_active = False
                            spawn_power_ups = False
                            first_spawn = True

                            # Call the method using the predetermined arguments
                            power_up_call[0](*power_up_call[1])

                elif CompPowerUp.is_active:

                    # Retrieve the method and arguments
                    power_up_call = comp_power_ups[CompPowerUp.power_up]

                    # If the power_up is just collected, start the timer
                    if first_collection:

                        first_collection = False
                        start_time = time()

                        # Call the method using the predetermined arguments
                        power_up_call[0](*power_up_call[1])

                    else:

                        end_time = time()
                        elapsed = end_time - start_time

                        if elapsed >= 5:

                            first_collection = True
                            CompPowerUp.is_active = False
                            spawn_power_ups = False
                            first_spawn = True

                            # Call the method using the predetermined arguments
                            power_up_call[0](*power_up_call[1])
                            

            # for row in grid:

            #     for square in row:

            #         square.draw()

            User_Paddle.move_paddle()

            if scorer:

                if trigger_delay == True:

                    delay_start = time()
                    scoring_sfx.play()
                    Scoreboard_Display.update_score(scorer)
                    trigger_delay = False

                delay_end = time()
                delay_elapsed = delay_end - delay_start
                Puck_Display.velocity = np.array([0,0])
                Computer_Paddle.draw(Puck_Display)

                if delay_elapsed >= 2:

                    scorer = None
                    delay_elapsed = 0.0
                    trigger_delay = True
                    Puck_Display.reset()
                    Computer_Paddle.reset()

            else:

            
                User_Paddle.determine_vel()

                Puck_Display.update_pos(Comp_Goal, Player_Goal)
                # PlayerPowerUp.is_active = True
                # Puck_Display.test = True
                # Puck_Display.test_puck()
                
                paddle_collision = User_Paddle.check_puck_collision(Puck_Display)
                comp_paddle_collision = Computer_Paddle.check_puck_collision(Puck_Display)

                # Depending on the position of the puck, move the computer paddle accordingly

                if Puck_Display.position[1] > TABLE_HEIGHT / 2:

                    Computer_Paddle.hold_position(Puck_Display)


                else:

                    # Slow down the paddle if a collision occurs 

                    if comp_paddle_collision:

                        computer_counter = 0

                    else:

                        Computer_Paddle.vel_magnitude = 10

                        computer_counter += 1

                        if computer_counter >= 30:

                            Computer_Paddle.vel_magnitude = 200

                    Computer_Paddle.move_paddle(Puck_Display, Comp_Goal, Player_Goal)

                Computer_Paddle.draw(Puck_Display)


                if paddle_collision or comp_paddle_collision == True:

                    counter_paddle += 1
                    collision_sfx.play()
                    
                    if counter_paddle > 1:

                        paddle_collision = False

                else:

                    counter_paddle = 0


                x_collision, y_collision, goal_collision, collision_centre, goal_to_check = Puck_Display.check_wall_collision(Comp_Goal, Player_Goal)
                # print(x_collision, y_collision, goal_collision, collision_centre, goal_to_check)

                # To prevent registering a wall collision multiple times before the puck has actually moved off of the wall

                if x_collision == True:

                    counter_x += 1
                    collision_sfx.play()
                    
                    if counter_x > 1:

                        x_collision = False

                else:

                    counter_x = 0

                if y_collision == True:

                    counter_y += 1
                    collision_sfx.play()
                    
                    if counter_y > 1:

                        y_collision = False

                else:

                    counter_y = 0

                if goal_collision == True:

                    counter_edge += 1
                    collision_sfx.play()
                    
                    if counter_edge > 1:

                        goal_collision = False

                else:

                    counter_edge = 0

                if comp_paddle_collision:

                    Puck_Display.update_velocity(Computer_Paddle, comp_paddle_collision, x_collision, y_collision, goal_collision, 
                                                 collision_centre, Player_Goal, Comp_Goal)

                else:

                    Puck_Display.update_velocity(User_Paddle, paddle_collision, x_collision, y_collision, goal_collision, 
                                                 collision_centre, Player_Goal, Comp_Goal)

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

    

