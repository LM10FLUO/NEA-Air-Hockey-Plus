# Importing .py files
import computer_classes
from goal_classes import Goal
import paddle_classes
import puck_classes
from power_up_classes import PowerUp
from icon_classes import Icon
import scoreboard_classes
import grid_classes

# Importing libraries
import pygame
import numpy as np
from sys import exit
from math import sqrt, inf
from time import sleep, time
from random import randint, choice

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

# Flags

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

pygame.mixer.init()
collision_sfx = pygame.mixer.Sound("Audio/collision_sfx (1)-[AudioTrimmer.com].mp3")
collision_sfx.set_volume(0.5)
scoring_sfx = pygame.mixer.Sound("Audio/scoring_sfx (1) (1)-[AudioTrimmer.com].mp3")
scoring_sfx.set_volume(0.5)

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



Red_Paddle_Icon = Icon(position=(400, 652), image_file="icons/red_paddle.png", scale=0.5)
Blue_Paddle_Icon = Icon(position=(400, 652), image_file="icons/blue_paddle.png", scale=0.5)
Green_Paddle_Icon = Icon(position=(400, 652), image_file="icons/green_paddle.png", scale=0.5)
Purple_Paddle_Icon = Icon(position=(400, 652), image_file="icons/purple_paddle.png", scale=0.5)

Paddles = [(Red_Paddle_Icon, "red"), (Blue_Paddle_Icon, "blue"), (Green_Paddle_Icon, "green"), (Purple_Paddle_Icon, "purple")]

# Instatiating objects

Table_Display = Table()
TABLE_HEIGHT = Table_Display.height
TABLE_WIDTH = Table_Display.width

Puck = puck_classes.Puck(image_file="red_puck.png", scale=0.4, table_dimensions=(TABLE_WIDTH, TABLE_HEIGHT))
User_Paddle = paddle_classes.Paddle(image=Red_Paddle_Icon.image, colour="red")

Comp_Goal = Goal(281, -90, "computer")
Player_Goal = Goal(281, 830, "player")

PlayerPowerUp = PowerUp((0, TABLE_WIDTH, TABLE_HEIGHT / 2, TABLE_HEIGHT), player="player")
CompPowerUp = PowerUp((0, TABLE_WIDTH, 0, TABLE_HEIGHT / 2), player="computer")

Scoreboard = scoreboard_classes.Scoreboard(p_position=(680,210), comp_position=(680,630), font_file="Fonts/Grand9K Pixel.ttf", font_size=100)

# Initialise pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Hockey Plus")
clock = pygame.time.Clock()

if __name__ == "__main__":

    while True:

        if first_run:

            path = None
            path_finished = False

            Computer_Paddle = computer_classes.Computer_Hard(image_file="icons/blue_paddle.png", 
                                                               half_dimensions=(TABLE_WIDTH, TABLE_HEIGHT // 2))
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
            counter = 0

        # Create a new path every 5th frame
        Table_Display.draw(screen)

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

        puck_predicted = Puck.predict_pos(
            Computer_Goal=Comp_Goal, 
            Player_Goal=Player_Goal,
            table_dimensions=(TABLE_WIDTH, TABLE_HEIGHT))
        
        # If the puck is actually in the opponent half, reset the path to None

        # if Puck.position[1] > TABLE_HEIGHT // 2:

        #     path = None

        # If the puck is predicted to be in the player's half, start to hold its position to anticipate movement

        if puck_predicted[1] > TABLE_HEIGHT // 2:

            Computer_Paddle.hold_position(Puck)
            path = None

        # If the puck is in the user's half, do not waste time pathfinding and hold the computer's position to anticipate
        elif puck_predicted[1] < TABLE_HEIGHT // 2 and scorer is None:

            if counter % 1 == 0:

                # If there is already of path and the puck is moving towards the puck, do not update the pathfinding

                # print(path)
                # print(path_finished)
                # print(f"Computer center = {Computer_Paddle.rect.center}\nPuck center = {Puck.rect.center}")
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

        Scoreboard.draw(screen)
        Comp_Goal.draw(screen)
        Player_Goal.draw(screen)

        User_Paddle.move_paddle(screen, (TABLE_WIDTH, TABLE_HEIGHT))

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

                scorer = None
                delay_elapsed = 0.0
                trigger_delay = True
                Puck.reset()
                Computer_Paddle.reset()
                path = None

        else:
        
            User_Paddle.determine_vel()

            Puck.update_pos(screen, Comp_Goal, Player_Goal)

            if path is not None:
            
                path, top_pointer, path_finished = Computer_Paddle.move_paddle(Puck, path, top_pointer, path_finished)
                # print(top_pointer)

            counter += 1

            Computer_Paddle.draw(screen)

            user_collision = User_Paddle.check_puck_collision(Puck)
            computer_collision = Computer_Paddle.check_puck_collision(Puck)

            if user_collision or computer_collision:

                counter_paddle += 1
                
                if counter_paddle > 1:

                    user_collision = False
                    computer_collision = False

                else:

                    collision_sfx.play()

            else:

                counter_paddle = 0

            x_collision, y_collision, goal_collision, collision_centre, goal_to_check = Puck.check_wall_collision(
                Comp_Goal, Player_Goal, (TABLE_WIDTH, TABLE_HEIGHT))

            if x_collision == True:

                counter_x += 1
                
                if counter_x > 1:

                    x_collision = False

                else:

                    collision_sfx.play()

            else:

                counter_x = 0

            if y_collision == True:

                counter_y += 1
                
                if counter_y > 1:

                    y_collision = False

                else:

                    collision_sfx.play()

            else:

                counter_y = 0

            if goal_collision == True:

                counter_edge += 1
                
                
                if counter_edge > 1:

                    goal_collision = False
                    
                else:

                    collision_sfx.play()

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

        

