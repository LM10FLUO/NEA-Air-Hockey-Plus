from pygame import image, transform, mask, mouse, display, draw, mixer
from numpy import array, round, linalg, ndarray, dot, sign
from math import sqrt
import pygame

# Initialise pygame
pygame.init()
screen = display.set_mode((800, 800))

class Puck:

    def __init__(self, image_file: str, scale: float, table_dimensions: tuple) -> None:

        temp_image = image.load(image_file)
        self.image = transform.scale_by(temp_image, scale)
        self.rect = self.image.get_rect()
        self.glow_colour = (0, 0, 0, 0)
        
        self.mask = mask.from_surface(self.image)

        self.position = array([282, 413]).astype(int)
        self.previous_pos = array([282, 413]).astype(int)
        self.height = self.image.get_height()
        self.width = self.image.get_width()

        self.rect.center = tuple(self.position)

        self.velocity = array([0,0]).astype(int)
        self.max_vel = 1500
        self.deceleration = 0.9999

        self.test = False
        self.top_left_valid = ( 5 + int(self.width / 2) , 5 + int(self.width / 2) )

        table_width, table_height = table_dimensions
        self.bottom_right_valid = ( table_width - int(self.width / 2) - 5, table_height - int(self.width / 2) - 5 )


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

        self.position = array([282, 413]).astype(int)
        self.velocity = array([0,0]).astype(int)

    def draw(self, screen):

        screen.blit(self.image, (self.position[0]-self.width/2, self.position[1]-self.height/2))

    # Subroutine for testing, allowing me to move the puck with my cursor

    def test_puck(self, screen: display) -> None:

        mouse_pos = mouse.get_pos()

        # Ensure that the rectangular hitbox of the puck aligns with the position of the puck image currently
        self.rect.center = mouse_pos
        self.position = mouse_pos
        draw.rect(screen, (0,0,0), self.rect, 1)

        screen.blit(self.image, (mouse_pos[0]-self.width/2, mouse_pos[1]-self.height/2))

    # Subroutine to update the position of the puck and move it accordingly

    def update_pos(self, screen: display, Computer_Goal: object, Player_Goal: object, temp_velocity: ndarray = None, 
                   temp_position: ndarray = None, Paddle: object = None, predicted_position: ndarray = None) -> ndarray:

        # Check if a velocity is passed so that we can reuse this function for predicting position
        if temp_velocity is None:

            self.previous_pos = self.position.copy()
            puck_velocity = self.velocity
            position = self.position

        else:

            puck_velocity = temp_velocity
            position = temp_position
    

        # Calculate the distance that the puck should move in the time the frame lasts
        dt = 1 / 60
        position = position + dt * puck_velocity
        # print(f"Unrounded position is {position}")
        position = round(position, decimals=0)

        if temp_velocity is None:

            self.position = position

            # Display the glow to identify who the shot stopper power up is active for IF ACTIVE
            glow_surface = self.mask.to_surface(setcolor=self.glow_colour, unsetcolor=None)
            glow_surface = transform.scale_by(glow_surface, 1.3)

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

            # if paddle_collision == True:

            #     paddle_puck_vector = Paddle.position - self.position
            #     paddle_puck_vector_previous = Paddle.position - self.position


            #     # Before we register a collision, we need to reset the position of the puck so that it isn't inside the paddle
            #     # This would lead to errors later on 

            #     mag_vector = linalg.norm(paddle_puck_vector)

            #     # If their centres directly overlap, use the previous position of the puck to determine where to reset the puck
            #     if mag_vector == 0:

            #         paddle_puck_vector = paddle_puck_vector_previous
            #         mag_vector = linalg.norm(paddle_puck_vector)

            #     # If the puck moves past the centre in the frame before overlap, we need to reset it to the correct side of the paddle
                
            #     if sign(paddle_puck_vector)[0] == sign(paddle_puck_vector_previous)[0]:

            #         paddle_puck_vector[0] = -paddle_puck_vector[0]

            #     if sign(paddle_puck_vector)[1] == sign(paddle_puck_vector_previous)[1]:

            #         paddle_puck_vector[1] == -paddle_puck_vector[1]

            #     # Update the puck's position so that it doesn't lie inside the puck
            #     min_puck_paddle_distance = Paddle.rect.width / 2 + self.rect.width / 2

            #     self.position = self.position + paddle_puck_vector * (min_puck_paddle_distance / mag_vector)
            #     self.position = round(self.position, decimals=0)

            self.rect.center = tuple(self.position)
            draw.rect(screen, (0,0,0), self.rect, 1)

            screen.blit(glow_surface, (self.position[0] - int(glow_surface.get_width() / 2), self.position[1] - int(glow_surface.get_height() / 2)))
            screen.blit(self.image, (self.position[0] - int(self.width / 2), self.position[1] - int(self.height / 2)))

            # self.rect.center = tuple(self.position)

        return position

    

    def check_wall_collision(self, Computer_Goal: object, Player_Goal: object, table_dimensions: tuple, temp_position: ndarray = None) -> tuple:

        table_width, table_height = table_dimensions

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
        if temp_rect.left <= 9 or temp_rect.right >= (table_width - 9):
            x_collision = True

        if temp_rect.top <= 9 or temp_rect.bottom >= (table_height - 9):

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
                        goal_collision: bool, collision_centre: ndarray, Player_Goal: object, Computer_Goal: object,
                        temp_velocity: ndarray = None) -> ndarray:

        # So that we can extend this function to predict the position of the puck, we will have an optional parameter to base the velocity off of

        if temp_velocity is None:

            puck_velocity = self.velocity

        else:

            puck_velocity = temp_velocity
            
        if paddle_collision == True:

        #     paddle_puck_vector = Paddle.position - self.position
        #     paddle_puck_vector_previous = Paddle.position - self.position


        #     # Before we register a collision, we need to reset the position of the puck so that it isn't inside the paddle
        #     # This would lead to errors later on 

        #     mag_vector = linalg.norm(paddle_puck_vector)

        #     # If their centres directly overlap, use the previous position of the puck to determine where to reset the puck
        #     if mag_vector == 0:

        #         paddle_puck_vector = paddle_puck_vector_previous
        #         mag_vector = linalg.norm(paddle_puck_vector)

        #     # If the puck moves past the centre in the frame before overlap, we need to reset it to the correct side of the paddle
            
        #     if sign(paddle_puck_vector)[0] == sign(paddle_puck_vector_previous)[0]:

        #         paddle_puck_vector[0] = -paddle_puck_vector[0]

        #     if sign(paddle_puck_vector)[1] == sign(paddle_puck_vector_previous)[1]:

        #         paddle_puck_vector[1] == -paddle_puck_vector[1]

        #     # Update the puck's position so that it doesn't lie inside the puck
        #     min_puck_paddle_distance = Paddle.rect.width / 2 + self.rect.width / 2

        #     self.position = self.position + paddle_puck_vector * (min_puck_paddle_distance / mag_vector)
        #     self.position = round(self.position, decimals=0)
        #     self.rect.center = tuple(self.position)

            # Determine the normal to the paddle to reflect the puck off of
            normal = array(self.rect.center) - array(Paddle.rect.center)
            magnitude = linalg.norm(normal)

            # Find the unit vector of the normal line
            unit_normal = normal / magnitude

            # Calculate the new velocity of the puck
            puck_velocity = puck_velocity - 2 * dot(puck_velocity-Paddle.velocity, unit_normal) * unit_normal
            puck_velocity = round(puck_velocity, decimals=0)

        if goal_collision == True:

            # Reflect the puck correctly off of the corner of the goal
            normal = array(self.rect.center) - collision_centre
            magnitude = linalg.norm(normal)

            # Find unit vector of the normal line
            unit_normal = normal / magnitude
            
            # Reflect the puck's movement
            puck_velocity = puck_velocity - 2 * dot(puck_velocity, unit_normal) * unit_normal
            puck_velocity = round(puck_velocity, decimals=0)

        if x_collision == True:

            puck_velocity[0] = int(-puck_velocity[0] * 0.9)

        if y_collision == True:

            puck_velocity[1] = int(-puck_velocity[1] * 0.9)

        # Decellerate the puck due to friction

        puck_velocity = puck_velocity * self.deceleration
        puck_velocity = round(puck_velocity, decimals=0)

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
        vel_magnitude = linalg.norm(puck_velocity)

        if vel_magnitude > self.max_vel:
            
            puck_velocity = puck_velocity / vel_magnitude * self.max_vel
            puck_velocity = round(puck_velocity, decimals=0)

        if self.test:

            puck_velocity = array([0,0])

        # If the velocity was not given, update the actual velocity of the puck
        if temp_velocity is None:

            self.velocity = puck_velocity


        return puck_velocity
    
    # Subroutine to predict the position of the puck a few frames ahead

    def predict_pos(self, Computer_Goal: object, Player_Goal: object, table_dimensions: tuple) -> ndarray:

        # We want to calculate the distance travelled per frame - at 60 fps, this means a frame runs for 1/60 of a second
        dt = 1 / 60

        # Flags for keeping track of whether collisions have already been registered and accounted for

        counter_x = 0
        counter_y = 0
        counter_edge = 0

        # As we only want to predict the position, we will hold velocity and position temporarily as to not move the actual puck
        current_velocity = self.velocity.copy()
        new_position = self.position.copy()

        # We will be predicting 20 frames ahead to give the computer some "reaction time" to the movement of the puck
        for i in range(20):

            # Check if there are any collisions in this new position to correctly predict the velocity and future puck position
            x_collision, y_collision, goal_collision, collision_centre, goal_to_check = self.check_wall_collision(Computer_Goal=Computer_Goal, 
                                                                                                                  Player_Goal=Player_Goal, 
                                                                                                                  temp_position=new_position,
                                                                                                                  table_dimensions=table_dimensions)
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
            
            new_position = self.update_pos(screen=screen, Computer_Goal=Computer_Goal, Player_Goal=Player_Goal, temp_velocity=current_velocity, temp_position=new_position)

        return new_position
    
    # So that we don't affect the other computer difficulties' functionalities, I will handle obstacle collisions as a separate function

    def check_obstacle_collision(self, Obstacle: object) -> ndarray:

        # I will be taking a different approach where I will be using mask and rect collisions due to the different shapes
        obstacle_collision = False
        collision_point = None


        # Check rect first as it is faster than checking mask collisions
        if self.rect.colliderect(Obstacle.rect):

            # Check for mask overlap, finding the first point of collision
            # As the obstacle is a square, we can more easily find the coordinate of intersection
            collision_point = Obstacle.mask.overlap(other=self.mask, offset=(self.rect.x - Obstacle.rect.x, self.rect.y - Obstacle.rect.y))

            if collision_point:

                obstacle_collision = True
                collision_point = array(collision_point) + array(Obstacle.rect.topleft)

        return obstacle_collision, collision_point

    def obstacle_collision(self, collision_point: ndarray):

        normal = self.position - collision_point
        magnitude = linalg.norm(normal)

        # Find the unit vector of the normal line
        unit_normal = normal / magnitude

        # Calculate the new velocity of the puck
        self.velocity = self.velocity - 2 * dot(self.velocity, unit_normal) * unit_normal
        self.velocity = round(self.velocity, decimals=0)

