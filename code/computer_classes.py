from pygame import display, image, transform, mask
import pygame
from numpy import array, round, linalg, full, ndarray
from math import sqrt
from heap_classes import Heap
from random import randint
from itertools import chain
from time import sleep, time

import grid_classes
import puck_classes
import goal_classes


class Computer_Easy:

    def __init__(self, image_file: str, half_dimensions: tuple):

        image_loaded = image.load(image_file)
        self.image = transform.scale_by(image_loaded, 0.5)
    
        self.rect = self.image.get_rect()
        self.mask = mask.from_surface(self.image)
        self.radius = self.rect.width / 2

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_magnitude = 50
        self.velocity = array([0,0])
        self.position = array([282, 150])

        self.colour = "blue"

        # Flag to disable movement if frozen:
        self.frozen = False

        # Flag to check if the power shot power up is active
        self.power_shot = False

        self.top_left_valid = ( 5 + int(self.width / 2) , 5 + int(self.width / 2) )

        half_width, half_height = half_dimensions
        self.bottom_right_valid = ( half_width - int(self.width / 2) - 5, half_height - int(self.width / 2) - 5 )

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
    def move_paddle(self, Puck: object, Computer_Goal: object, Player_Goal: object, table_dimensions: tuple) -> None:

        # If frozen, prevent the paddle from moving

        if self.frozen:

            self.velocity = array([0,0])

        elif not self.frozen:

            # Time a frame lasts to calculate the maximum distance the computer can travel in a frame
            dt = 1 / 60
            self.vel_magnitude = 500
            avoid = False   # Flag to determine whether the puck is likely to get trapped
            table_width, table_height = table_dimensions

            # Work out the direction needed to move the paddle in to meet the puck
            predicted_pos = Puck.predict_pos(Computer_Goal, Player_Goal)

            # If the puck is going to be cornered, force the computer to move away from the puck, adding a buffer to give the paddle time to move out the way

            if (Puck.position[0] <= Puck.top_left_valid[0] + 10 or Puck.position[0] >= Puck.bottom_right_valid[0] - 10 
                or Puck.position[1] <= Puck.top_left_valid[1] + 10):

                avoid = True
                predicted_pos = array([282,150])
            
            # Calculate the velocity the computer needs to travel at to move towards the puck
            direction_vector = predicted_pos - self.position
            direction_magnitude = linalg.norm(direction_vector)
            self.velocity = (self.vel_magnitude / direction_magnitude) * direction_vector
            self.velocity = round(self.velocity, decimals=0)

            # Update the position of the paddle
            
            # Save previous conditions and attributes to reset if problematic movement is detected
            previous_puck_collision = self.check_puck_collision(Puck)
            previous_position = self.position.copy()

            self.position = self.position + self.velocity * dt
            self.position = round(self.position, decimals=0)
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

                elif self.position[0] > (table_width - int(self.width / 2) - 5):
                    self.position[0] = (table_width - int(self.width / 2) - 5)

                if self.position[1] < (5 + int(self.width/2)):
                    self.position[1] = (5 + int(self.width/2))

                elif self.position[1] > (table_height / 2 - int(self.width / 2)):
                    self.position[1] = (table_height / 2 - int(self.width / 2))

            

    def reset(self) -> None:

        self.position = array([282, 150])
        self.velocity = array([0,0])

    def draw(self, screen: display) -> None:

        screen.blit(self.image, (self.position[0]-self.width/2, self.position[1]-self.height/2))
        pygame.draw.rect(screen, (0,0,0), self.rect, 1)

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

            vel_magnitude = linalg.norm(self.velocity)

            if vel_magnitude == 0:

                self.velocity = array([0,0])

            else:

                self.velocity = self.velocity / vel_magnitude * self.vel_magnitude
                self.velocity = round(self.velocity, decimals=0)

            # Update the velocity accordingly
            self.position = self.position + self.velocity * dt
            self.position = round(self.position, decimals=0)

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

    def __init__(self, image_file: str, half_dimensions: tuple) -> None:

        super().__init__(image_file, half_dimensions)
        self.puck_squares = full(100, None)
        self.current_predicted = None

    def find_path(self, grid: list, start_coordinates: tuple, target_coordinates: tuple) -> list:

        # Edge case: if the start and target are the same, do not create a path
        if start_coordinates == target_coordinates:

            return None

        # Open list - these are the nodes yet to be explored
        # This will use a min heap priority queue to efficiently explore the next node with minimum f cost
        open = Heap(full(1000, None))

        # Closed list for already discovered nodes
        closed = []

        # Initially set the start_node costs to 0
        start_node = grid[start_coordinates[0]][start_coordinates[1]]
        start_node.pointer = array([None, None])
        start_node.g_cost, start_node.h_cost, start_node.f_cost = 0, 0, 0

        current_node = start_node

        target_node = grid[target_coordinates[0]][target_coordinates[1]]

        while current_node is not None:

            if target_coordinates in current_node.neighbours:

                target_node.pointer = current_node.position
                current_node = None
                continue

            else:

                for neighbour_coordinates in current_node.neighbours:

                    # Ignore any obstacle squares - we cannot traverse these
                    neighbour = grid[neighbour_coordinates[0]][neighbour_coordinates[1]]

                    # For visual testing, I will update the colour of the 

                    if neighbour.is_obstacle or neighbour.is_perm_obstacle:

                        continue

                    else:

                        neighbour.is_discovered = True

                        # The g_cost will also include a weight, indicating whether this square is a preferred route
                        g_cost = current_node.g_cost + neighbour.weight + linalg.norm(
                            array(neighbour.rect.center) - array(current_node.rect.center))

                        # As the h_cost is constant, instead of comparing f_costs, we can just compare g_costs of the previous and current paths
                        # If the g_cost of the current path is lower, a better path to this square has been found
                        if g_cost < neighbour.g_cost:

                            neighbour.g_cost = g_cost

                            # Calculate the heuristic - i.e. the "most optimistic estimate"
                            neighbour.h_cost = linalg.norm(array(target_node.rect.center) - array(neighbour.rect.center))

                            neighbour.f_cost = neighbour.g_cost + neighbour.h_cost

                            # Now we have found a better path, redirect the pointer of the neighbour to the current node
                            neighbour.pointer = current_node.position

                            # If the neighbour has not yet been "discovered", add it to open with its costs evaluated
                            if neighbour not in closed and neighbour not in open.heap:
                            
                                open.insert(neighbour)

                            # If the node has already been explored, reopen the node - this will be useful for GAA*
                            elif neighbour in closed:

                                closed.remove(neighbour)
                                open.insert(neighbour)

                closed.append(current_node)
                current_node = open.extract()

        # Now that we have gotten to the target node, backtrack to find the completed path

        path = full(50, None, dtype=object)
        path[0] = target_node
        
        # To avoid the need to use the append function on a list which is very slow, we will use an end pointer to keep track
        # of the next available index we can write to - i.e. a stack implementation
        end_pointer = 1
        next_coordinates = target_node.pointer

        while next_coordinates[0] is not None:

            next_node = grid[next_coordinates[0]][next_coordinates[1]]
            
            path[end_pointer] = next_node
            next_coordinates = next_node.pointer
            end_pointer += 1

        return path, end_pointer - 1

    # Procedure to find the squares the puck occupies

    def find_puck(self, Puck: object, grid: list, predicted_position: ndarray) -> None:

        self.puck_squares.fill(None)
        # First we need to flatten the 2D grid to create a 1D list of object
        object_list = list(chain.from_iterable(grid))
        rect_list = [square_object.rect for square_object in object_list]

        # We will increase the collision space of the puck to ensure no accidental collisions between puck and paddle
        enlarge_factor = ((Puck.rect.width + self.rect.width / 2)) / Puck.rect.width
        collision_space = transform.scale_by(Puck.image, enlarge_factor)
        collision_rect = collision_space.get_rect()
        collision_mask = mask.from_surface(collision_space)

        collision_rect.center = tuple(predicted_position)

        # Find all the square that intersect in the rect
        potential_collisions = collision_rect.collidelistall(rect_list)
        potential_list = [object_list[index] for index in potential_collisions]

        puck_x, puck_y = collision_rect.x, collision_rect.y
        counter = 0

        # Check for mask collisions
        for square in potential_list:

            # We need to find the offset between the two masks - i.e. we need to "reposition" the masks to correspond
            # with their actual position in order to test for the overlap

            if collision_mask.overlap(other=square.mask, offset=(square.rect.x - puck_x, square.rect.y - puck_y)):

                square.is_obstacle = True
                self.puck_squares[counter] = square
                counter += 1

        

    def attack(self, Puck: object, Computer_Goal: object, Player_Goal: object, grid: list, table_dimensions: tuple,
               predicted_position: ndarray) -> tuple:

        # predicted_pos = Puck.predict_pos(Computer_Goal, Player_Goal)

        self.current_predicted = predicted_position

        # We will randomly decide where we want to shoot the puck 
        # n.b. / 2 so that it will enter the goal and not collide with the post of the goal
        random_x = randint(int(Player_Goal.left_corner[0] + Puck.rect.width / 2), 
                           int(Player_Goal.right_corner[0] - Puck.rect.width / 2)) 
        
        target_pos = array([random_x, Player_Goal.left_corner[1]])

        # I want to extend the line behind the puck, therefore I will be using vector math to calculate the point of origin
        direction_vector = target_pos - self.current_predicted
        mu = -self.current_predicted[1] / direction_vector[1]
        extended_x = self.current_predicted[0] + mu * direction_vector[0]
        extended_x = array([extended_x, 0])
        extended_x = round(extended_x, decimals=0)

        # We want to draw a line connecting the two points and see which squares this line intersects

        target_square = None

        for row in grid:

            for square in row:

                # If the line intersects the square and the square is not an obstacle, decrease the weight of the square
                if square.rect.clipline(target_pos, extended_x) and not square.is_obstacle:
                        
                        if square.rect.center[1] < (self.current_predicted[1] - 70):

                            square.weight = 0
                            square.weight_decreased = True

                        # We will identify the target square that is the closest valid point along the aimed path to the collision space
                        if (target_square is None or square.rect.y > target_square.rect.y) and square.rect.center[1] < self.current_predicted[1]:

                            target_square = square
                    
        if target_square is not None:

            target_square.is_target = True

            return target_square.position

    def defend(self, Puck: object, grid: list) -> None:

        self.current_predicted = Puck.position

        # Reset the weighted squares - aiming is no longer a priority
        for row in grid:

            for square in row:

                if square.weight_decreased == True:

                    square.weight_decreased = False
                    square.weight = 50


        counter = 0

        # We just want to collide with the puck as soon as possible in order to clear the puck
        # Therefore we will allow the puck to move into the collision space
        while self.puck_squares[counter] is not None:

            if self.puck_squares[counter].rect.y < self.current_predicted[1]:

                self.puck_squares[counter].is_obstacle = False

            counter += 1
 
    # Here we are overriding the move_paddle procedure from the Computer_Easy class

    def move_paddle(self, Puck: object, path: ndarray, top_pointer: int, path_finished: bool) -> tuple:

        # Calculate the max distance along the path the computer can move to avoid jerky movement
        dt = 1 / 60
        max_distance = self.vel_magnitude * dt
        total_traversed = 0

        # If the path has already been fully traversed, follow through
        if top_pointer == -1:

            self.position = self.position + self.velocity * dt 
            self.position = round(self.position, decimals=0)
            self.rect.center = tuple(self.position)
            path_finished = True

        else:

            # Now we keep moving along the path until we reach a "realistic" distance that can be traversed by the paddle in one frame
            while total_traversed <= max_distance:

                # If the stack is empty, then keep the paddle moving with its current_velocity
                if top_pointer < 0:

                    distance_left = max_distance - total_traversed
                    distance_vector = self.velocity * dt
                    factor = distance_left / linalg.norm(distance_vector)
                    distance_to_cover = round(distance_vector * factor, decimals=0)
                    self.position = self.position + distance_to_cover
                    self.rect.center = tuple(self.position)

                    # Exit the loop
                    total_traversed = max_distance + 1
                    path_finished = True

                # We will traverse the path by popping off the top of the "stack" to get from the start square to the target
                else:

                    next_square = path[top_pointer]
                    distance_vector = array(next_square.rect.center) - self.position

                    mag_distance = linalg.norm(distance_vector)
                    total_traversed += mag_distance

                    self.position = array(next_square.rect.center)
                    self.rect.center = tuple(self.position)

                    # Calculate the current velocity of the paddle
                    self.velocity = distance_vector / dt
                    mag_velocity = linalg.norm(self.velocity)

                    # If the computer collides with the puck, the path has been finished
                    if self.rect.colliderect(Puck.rect):

                        # If the rectangular hitboxes collide, check if the actual objects collide using masks
                        offset_x, offset_y = Puck.rect.x - self.rect.x, Puck.rect.y - self.rect.y 

                        # If the masks do in fact overlap, then move the puck so that it doesn't overlap with the paddle
                        if self.mask.overlap(Puck.mask, (offset_x, offset_y)):

                            centre_vector = self.position - Puck.position
                            max_centre_distance = Puck.rect.width / 2 + self.rect.width / 2
                            centre_magnitude = linalg.norm(centre_vector)

                            # Reposition the puck so that it is now outside of the paddle's hitbox
                            self.position = Puck.position + (centre_vector * (max_centre_distance / centre_magnitude))
                            self.rect.center = tuple(self.position)

                            return path, top_pointer, path_finished

                    # Avoid divide by 0 errors
                    if mag_velocity != 0:

                        self.velocity = self.velocity * (self.vel_magnitude / mag_velocity)

                    top_pointer -= 1

        # Check if the computer's final position is valid

        if self.position [0]< (self.top_left_valid[0] + self.rect.width / 2): 
        
            self.position[0] = self.top_left_valid[0] + self.width / 2
            
        elif self.position[0] > (self.bottom_right_valid[0] - self.width / 2):

            self.position[0] = self.bottom_right_valid[0] - self.width / 2

        if self.position[1] < (self.top_left_valid[1] + self.rect.height / 2): 
        
            self.position[1] = self.top_left_valid[1] + self.height / 2
            
        elif self.position[1] > (self.bottom_right_valid[1] - self.height / 2):

            self.position[1] = self.bottom_right_valid[1] - self.height / 2

        self.rect.center = tuple(self.position)

        return path, top_pointer, path_finished

    # Check whether the computer paddle is moving towards the puck
    def paddle_trajectory(self, Puck: object, table_dimensions: tuple, screen: display) -> bool:

        # Check the line that the puck is moving along
        table_width, table_height = table_dimensions

        direction_vector = self.velocity

        # To avoid divide by zero errors
        if direction_vector[1] == 0:

            return True

        mu1 = - self.position[1] / direction_vector[1]
        mu2 = (table_height - self.position[1]) / direction_vector[1] 

        top_point = array([(self.position[0] + mu1 * direction_vector)[0], 0])
        bottom_point = array([(self.position[0] + mu2 * direction_vector)[0], table_height])

        pygame.draw.line(screen, (255,0,0), tuple(top_point), tuple(bottom_point), 5)

        # Check if the computer is moving towards the puck

        if Puck.rect.clipline(tuple(bottom_point), tuple(top_point)) and Puck.position[1] < table_height // 2:

            return True
        
        else:

            return False



if __name__ == "__main__":

    grid = grid_classes.create_grid(800, 800)

    # Initialise pygame
    pygame.init()
    screen = display.set_mode((800, 800))
    display.set_caption("Grid Testing")
    screen.fill((255,255,255))

    Computer = Computer_Medium("icons/red_paddle.png", (800, 800))
    Puck = puck_classes.Puck("red_puck.png", 0.4, (800, 800))
    Computer_Goal = goal_classes.Goal(281, -90, "computer")
    Player_Goal = goal_classes.Goal(281, 780, "player")

    Puck.position = array([300, 300])
    counter = 0


    while True:

        # screen.fill((255,255,255))
        Computer.find_puck(Puck, grid, (200, 200))
        # Computer.defend(Puck, grid)

        # Create a new path every 5th frame

        if counter % 5 == 0:

            for row in grid:

                for square in row:

                    square.reset()

            attack_values = Computer.attack(Puck, Computer_Goal, Player_Goal, grid, (800, 800), (200, 200))
            if attack_values is not None:

                target_x, target_y = attack_values

            # computer_squares = Computer.position // 10
            # computer_squares = computer_squares.astype(int)

            # path_output = Computer.find_path(grid, (computer_squares[0], computer_squares[1]), (target_x, target_y))

            # if path_output is not None:

            #     path, top_pointer, path_finished = path_output

            # for square in path:

            #     if square is None:

            #         break

            #     else:

            #         square.is_discovered = False
            #         square.is_path = True

        for row in grid:

            for square in row:

                square.draw(screen)


        # if path_output is not None:
        #   path, top_pointer = Computer.move_paddle(path, top_pointer)
        #   Computer.draw(screen)


        Puck.test_puck(screen)
        Computer_Goal.draw(screen)
        Player_Goal.draw(screen)

        
        


        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

        counter += 1

        pygame.display.update()


                            