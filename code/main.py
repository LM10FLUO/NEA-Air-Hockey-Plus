# Importing .py files
import computer_classes
from goal_classes import Goal
import paddle_classes
import puck_classes
from power_up_classes import PowerUp
from icon_classes import Icon
import scoreboard_classes
import grid_classes
import obstacle_classes
import interface_classes

# Importing libraries
import pygame
import numpy as np
from sys import exit
from time import time
from pygame import display

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
win: bool = False
loss: bool = False

difficulty: int = 1
paddle_colour: int = 0

max_score: int = 10

first_run: bool = True
first_collection: bool = True
first_spawn: bool = True

counter_x: int = 0
counter_y: int = 0
counter_edge: int = 0
counter_paddle: int = 0 
counter: int = 0
computer_counter: int = 0 
counter_obstacle: int = 0

scorer: str = None

start_time: float = None
end_time: float = None
start_clock: bool = True

delay_start: float = None
delay_end: float = None
delay_elapsed: float = 0.0
trigger_delay: bool = True

display_obstacle: bool = False
spawn_power_ups: bool = False

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Hockey Plus")
clock = pygame.time.Clock()

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

class Text:

    def __init__(self, position: tuple, font_file: str, font_size: int, text: str) -> None:

        self.text = text
        self.position = position
        self.font = pygame.font.Font(font_file, font_size)

    def draw(self) -> None:

        text_display = self.font.render(self.text, True, RED, None)
        text_rect = text_display.get_rect()
        text_rect.center = (self.position[0], self.position[1])

        screen.blit(text_display, ((self.position[0] - text_rect.width/2), (self.position[1] - text_rect.height/2)))

# Instatiating objects
Interface_Screens = interface_classes.Interface_Screens(title_path="interface_screens/Air_Hockey_Home_Scree.png",
                                                        settings_path="interface_screens/Settings_Screen.png",
                                                        loss_path="interface_screen/Losing_Screen.png",
                                                        win_path="interface_screens/Winning_Screen.png",
                                                        height=800)

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

Restart_Button = Button(position=(284, 661), image_file="buttons/Restart_Button.png", scale=0.5)
Home_Button = Button(position=(516, 661), image_file="buttons/Home_Button.png", scale=0.5)

Player_Score = Text(position=(556, 413), font_file="Fonts/Grand9K Pixel.ttf", font_size=100, text="")
Computer_Score = Text(position=(284, 413), font_file="Fonts/Grand9K Pixel.ttf", font_size=100, text="")

        
Score_Input = TextBox(position=(400, 480), font_file="Fonts/Grand9K Pixel.ttf", font_size=50, user_input="10")

Paddles = [(Red_Paddle_Icon, "red"), (Blue_Paddle_Icon, "blue"), (Green_Paddle_Icon, "green"), (Purple_Paddle_Icon, "purple")]
Difficulties = [[Easy_Icon, Easy_Letters], [Medium_Icon, Medium_Letters], [Hard_Icon, Hard_Letters]]

Scoreboard = scoreboard_classes.Scoreboard(p_position=(680,210), comp_position=(680,630), font_file="Fonts/Grand9K Pixel.ttf", font_size=100)

Table_Display = Table()

TABLE_HEIGHT = Table_Display.height
TABLE_WIDTH = Table_Display.width

Puck = puck_classes.Puck(image_file="red_puck.png", scale=0.4, table_dimensions=(TABLE_WIDTH, TABLE_HEIGHT))

Comp_Goal = Goal(281, -90, "computer")
Player_Goal = Goal(281, 830, "player")

PlayerPowerUp = PowerUp((0, TABLE_WIDTH, TABLE_HEIGHT / 2, TABLE_HEIGHT), player="player")
CompPowerUp = PowerUp((0, TABLE_WIDTH, 0, TABLE_HEIGHT / 2), player="computer")


# Main game loop
if __name__ == "__main__":

    while True:

        # Title screen loop
        while run_title == True:
            
            Interface_Screens.display_title(screen=screen)

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

            Interface_Screens.display_settings(screen=screen)
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

            counter += 1
            

            # If the first run, instantiate the paddle and grid, preventing reinstantiation every loop
            if first_run:

                paddle_image = Paddles[paddle_colour][0].image
                User_Paddle = paddle_classes.Paddle(paddle_image, Paddles[paddle_colour][1])

                # EASY MODE

                if difficulty == 0:

                    Computer_Paddle = computer_classes.Computer_Easy("icons/blue_paddle.png", (TABLE_WIDTH, TABLE_HEIGHT // 2))

                elif difficulty == 1 or difficulty == 2:

                    # MEDIUM MODE

                    if difficulty == 1:

                        Computer_Paddle = computer_classes.Computer_Medium(image_file="icons/blue_paddle.png", 
                                                                    half_dimensions=(TABLE_WIDTH, TABLE_HEIGHT // 2))
                        
                    # HARD MODE

                    elif difficulty == 2:

                        Computer_Paddle = computer_classes.Computer_Hard(image_file="icons/blue_paddle.png", 
                                                               half_dimensions=(TABLE_WIDTH, TABLE_HEIGHT // 2))
                        Obstacles = obstacle_classes.Obstacle("icons/Obstacles/Obstacle.png")
                    
                    path = None
                    path_finished = False
                    path_output = None
                    
                    grid = grid_classes.create_grid(TABLE_WIDTH, TABLE_HEIGHT // 2)

                    # To take into account the collision space of the puck, we need to "shrink" the total area that is can pathfind with
                    # This means we will make squares close to the walls obstacles

                    for row in grid:

                        for square in row:

                            if (square.position[0] * 10) < (Computer_Paddle.width / 2) or (square.position[0] * 10) > (
                                TABLE_WIDTH - Computer_Paddle.width / 2):

                                square.is_perm_obstacle = True
                                
                            if (square.position[1] * 10) < (Computer_Paddle.width / 2) or (square.position[1] * 10) > (
                                TABLE_HEIGHT / 2 - Computer_Paddle.width / 2):

                                square.is_perm_obstacle = True


                user_power_ups = {"freeze": [PlayerPowerUp.freeze, (Computer_Paddle, None)],
                                "double_points": [PlayerPowerUp.double_points, (Scoreboard, None)],
                                "widen_goal": [PlayerPowerUp.widen_goal, (Comp_Goal, None)],
                                "enlarge_paddle": [PlayerPowerUp.enlarge_paddle, (User_Paddle, None)],
                                "shot_stopper": [PlayerPowerUp.shot_stopper, (User_Paddle, 
                                                                                Puck, 
                                                                                Player_Goal, 
                                                                                Scoreboard, 
                                                                                {"red": (255, 0, 0, 50), 
                                                                                "blue": (38, 247, 253, 50), 
                                                                                "green": (45, 254, 84, 50), 
                                                                                "purple": (191, 64, 191, 50)})],
                                "power_shot": [PlayerPowerUp.power_shot, (User_Paddle, None)]}
                
                comp_power_ups = {"freeze": [CompPowerUp.freeze, (User_Paddle, None)],
                                    "double_points": [CompPowerUp.double_points, (Scoreboard, None)],
                                    "widen_goal": [CompPowerUp.widen_goal, (Player_Goal, None)],
                                    "enlarge_paddle": [CompPowerUp.enlarge_paddle, (Computer_Paddle, None)],
                                    "shot_stopper": [CompPowerUp.shot_stopper, (Computer_Paddle, 
                                                                                Puck, 
                                                                                Comp_Goal, 
                                                                                Scoreboard,
                                                                                {"red": (255, 0, 0, 50), 
                                                                                "blue": (38, 247, 253, 50), 
                                                                                "green": (45, 254, 84, 50), 
                                                                                "purple": (191, 64, 191, 50)})],
                                    "power_shot": [CompPowerUp.power_shot, (Computer_Paddle, None)]}
                
                first_run = False

                
            Table_Display.draw(screen)
            Scoreboard.draw(screen)
            

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
                    PlayerPowerUp.draw(screen)
                    CompPowerUp.draw(screen)
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
                            
            if difficulty == 1:

                puck_predicted = Puck.predict_pos(
                    Computer_Goal=Comp_Goal, 
                    Player_Goal=Player_Goal,
                    table_dimensions=(TABLE_WIDTH, TABLE_HEIGHT))
            
                # If the puck is actually in the opponent half, reset the path to None

                # If the puck is predicted to be in the player's half, start to hold its position to anticipate movement

                if puck_predicted[1] > TABLE_HEIGHT // 2:

                    Computer_Paddle.hold_position(Puck)
                    path = None

                # If the puck is in the user's half, do not waste time pathfinding and hold the computer's position to anticipate
                elif puck_predicted[1] < TABLE_HEIGHT // 2 and scorer is None:

                    if counter % 1 == 0:

                        # If there is already of path and the puck is moving towards the puck, do not update the pathfinding

                        if path is None or path_finished == True:

                            path_finished = False

                            # print("entered")
                            # Find the collision space of the puck

                            for row in grid:

                                for square in row:

                                    square.reset()

                            Computer_Paddle.find_puck(Puck, grid, puck_predicted)

                            # for row in grid:

                            #     for square in row:

                            #         square.reset()

                            # Find the target square that we want to use to aim the computer's shot

                            attack_values = Computer_Paddle.attack(Puck, Player_Goal, grid, (TABLE_WIDTH, TABLE_HEIGHT), puck_predicted)

                            if Computer_Paddle.rect.center[1] > Puck.rect.center[1]:

                                Computer_Paddle.defend(grid, puck_predicted)
                                Computer_Paddle.find_puck(Puck, grid, Puck.position)

                            if attack_values is not None:

                                target_x, target_y = attack_values

                            # If the target position identified cannot be accessed, cancel the pathfinding algorithm to reduce unnecessary computation
                            if grid[target_x][target_y].is_perm_obstacle or attack_values is None:

                                grid[target_x][target_y].is_target = False
                                Computer_Paddle.hold_position(Puck)
                                path_output = None

                            # Otherwise find the shot path
                            else:

                                computer_squares = Computer_Paddle.position // 10
                                computer_squares = computer_squares.astype(int)

                                path_output = Computer_Paddle.find_path(grid, (computer_squares[0], computer_squares[1]), (target_x, target_y))

                                if path_output is not None:

                                    path, top_pointer = path_output

                                else:

                                    path = None

            elif difficulty == 2:

                if counter % 120 == 0:

                    Obstacles.reset()
                    Obstacles.spawn_obstacle(screen, grid, Puck, Computer_Paddle, Comp_Goal, (TABLE_WIDTH, TABLE_HEIGHT // 2))
                    display_obstacle = True

                puck_predicted = Puck.predict_pos(
                    Computer_Goal=Comp_Goal, 
                    Player_Goal=Player_Goal,
                    table_dimensions=(TABLE_WIDTH, TABLE_HEIGHT))
                
                # If the puck is actually in the opponent half, reset the path to None
                if scorer is None:

                    # If there is already of path and the puck is moving towards the puck, do not update the pathfinding

                    if path is None or path_finished == True:

                        path_finished = False

                        for row in grid:

                            for square in row:

                                square.reset()

                        # If the puck is in the player's half, anticipate its movement
                        if puck_predicted[1] > TABLE_HEIGHT // 2:

                            attack_values = Computer_Paddle.hold_position(Puck, Obstacles, grid)

                        else:


                            # Find the collision space of the puck

                            Computer_Paddle.find_puck(Puck, grid, puck_predicted)

                            # Find the target square that we want to use to aim the computer's shot

                            attack_values = Computer_Paddle.attack(Puck, Player_Goal, grid, (TABLE_WIDTH, TABLE_HEIGHT), puck_predicted)

                            if Computer_Paddle.rect.center[1] > Puck.rect.center[1]:

                                Computer_Paddle.defend(grid, puck_predicted)
                                Computer_Paddle.find_puck(Puck, grid, Puck.position)

                            if attack_values is not None:

                                target_x, target_y = attack_values

                        # If the target position identified cannot be accessed, cancel the pathfinding algorithm to reduce unnecessary computation
                        if grid[target_x][target_y].is_perm_obstacle:

                            grid[target_x][target_y].is_target = False
                            attack_values = Computer_Paddle.hold_position(Puck, Obstacles, grid)
                            path_output = None

                        # Decide how to move the computer based on current circumstances

                        if attack_values is not None:

                            target_x, target_y = attack_values

                            computer_squares = Computer_Paddle.position // 10
                            computer_squares = computer_squares.astype(int)

                            path_output = Computer_Paddle.find_path(grid, (computer_squares[0], computer_squares[1]), (target_x, target_y))

                            if path_output is not None:

                                path, top_pointer = path_output

                            else:

                                path = None

                    if path is not None:

                        for square in path:

                            if square is None:

                                break

                            else:

                                square.is_discovered = False
                                square.is_path = True

                    for row in grid:

                        for square in row:

                            square.draw(screen) 

            User_Paddle.move_paddle(screen, (TABLE_WIDTH, TABLE_HEIGHT))
            Comp_Goal.draw(screen)
            Player_Goal.draw(screen)

            if display_obstacle:

                Obstacles.draw(screen)

            if scorer:

                if trigger_delay == True:

                    delay_start = time()
                    scoring_sfx.play()
                    Scoreboard.update_score(scorer)
                    trigger_delay = False

                delay_end = time()
                delay_elapsed = delay_end - delay_start
                Puck.velocity = np.array([0,0])
                Computer_Paddle.draw(screen)

                if delay_elapsed >= 2:

                    outcome = Scoreboard.check_score(max_score)

                    scorer = None
                    delay_elapsed = 0.0
                    trigger_delay = True
                    Puck.reset()
                    Computer_Paddle.reset()
                    path = None
                    display_obstacle = False

                    if difficulty == 2:

                        Obstacles.reset()

                    if outcome == "win":

                        win = True
                        run_end = True
                        run_game = False
                        print("WIN")
                        continue

                    elif outcome == "loss":

                        loss = True
                        run_end = True
                        run_game = False
                        print("LOSS")
                        continue

            else:

                User_Paddle.determine_vel()
                Puck.update_pos(screen, Comp_Goal, Player_Goal)

                user_collision = User_Paddle.check_puck_collision(Puck)
                computer_collision = Computer_Paddle.check_puck_collision(Puck)

                if difficulty == 0:

                    # Depending on the position of the puck, move the computer paddle accordingly

                    if Puck.position[1] > TABLE_HEIGHT / 2:

                        Computer_Paddle.hold_position(Puck)

                    else:

                        # Slow down the paddle if a collision occurs 

                        if computer_collision:

                            computer_counter = 0

                        else:

                            Computer_Paddle.vel_magnitude = 10

                            computer_counter += 1

                            if computer_counter >= 30:

                                Computer_Paddle.vel_magnitude = 200

                        Computer_Paddle.move_paddle(Puck, Comp_Goal, Player_Goal, (TABLE_WIDTH, TABLE_HEIGHT))

                elif difficulty == 1 or difficulty == 2:

                    if path is not None:
                                
                            path, top_pointer, path_finished = Computer_Paddle.move_paddle(Puck, path, top_pointer, path_finished)
                
                Computer_Paddle.draw(screen)


                if user_collision or computer_collision:

                    counter_paddle += 1
                    
                    if counter_paddle > 1:

                        user_collision = False
                        computer_collision = False

                    else:

                        collision_sfx.play()

                else:

                    counter_paddle = 0
                    


                x_collision, y_collision, goal_collision, collision_centre, goal_to_check = Puck.check_wall_collision(Comp_Goal, Player_Goal, (TABLE_WIDTH, TABLE_HEIGHT))

                if display_obstacle:

                    obstacle_collision, collision_point = Puck.check_obstacle_collision(Obstacles)

                    if obstacle_collision:

                        counter_obstacle += 1

                        if counter_obstacle > 1:

                            obstacle_collision = False

                        else:

                            Puck.obstacle_collision(collision_point)
                            collision_sfx.play()

                    else:

                        counter_obstacle = False

                # To prevent registering a wall collision multiple times before the puck has actually moved off of the wall

                if difficulty == 2:

                    obstacle_collision, collision_point = Puck.check_obstacle_collision(Obstacles)

                    if obstacle_collision:

                        counter_obstacle += 1

                        if counter_obstacle > 1:

                            obstacle_collision = False

                        else:

                            Puck.obstacle_collision(collision_point)
                            collision_sfx.play()

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

                if computer_collision:

                    Puck.update_velocity(Computer_Paddle, computer_collision, x_collision, y_collision, goal_collision, 
                                                 collision_centre, Player_Goal, Comp_Goal)

                else:

                    Puck.update_velocity(User_Paddle, user_collision, x_collision, y_collision, goal_collision, 
                                                 collision_centre, Player_Goal, Comp_Goal)

                if goal_to_check:

                    scorer = goal_to_check.check_goal(Puck)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    exit()

            pygame.display.update()

            # We will be running the game at 60 fps
            clock.tick(60)

        while run_end:

            # Display the corresponding screen based on the outcome
            if win:
  
                Interface_Screens.display_win(screen)

            elif loss:

                Interface_Screens.display_loss(screen)

            # Display the final score
            Player_Score.text = str(Scoreboard.comp_score)
            Computer_Score.text = str(Scoreboard.p_score)

            Player_Score.draw()
            Computer_Score.draw()

            # If the buttons are pressed, reset the corresponding flags and variables

            home_input = Home_Button.draw()
            restart_input = Restart_Button.draw()

            if home_input or restart_input:

                run_end = False
                win = False
                loss = False

                first_run = True
                first_collection = True
                first_spawn = True

                counter_x  = 0
                counter_y  = 0
                counter_edge  = 0
                counter_paddle  = 0 
                counter  = 0
                computer_counter  = 0 
                counter_obstacle  = 0

                scorer = None

                start_time = None
                end_time = None
                start_clock = True

                delay_start = None
                delay_end = None
                delay_elapsed = 0.0
                trigger_delay = True

                display_obstacle = False
                spawn_power_ups = False

                Scoreboard.p_score = 0
                Scoreboard.comp_score = 0

                if restart_input:

                    run_game = True
                    print("Restarted")

                elif home_input:

                    run_title = True
                    difficulty  = 1
                    paddle_colour  = 0

                    max_score  = 10
                    print("Returned to home screen")

                


            # Handle quitting the game screen  
            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    exit()

            pygame.display.update()

        # Handle quitting the game screen  
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

    

