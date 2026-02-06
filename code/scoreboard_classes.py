from pygame import display, font, init

# Initialise pygame
init()
screen = display.set_mode((800, 800))

RED = (214, 73, 59)

# Class for the scoreboard

class Scoreboard:

    def __init__(self, p_position: tuple, comp_position: tuple, font_file:  str, font_size: int) -> None:

        self.font = font.Font(font_file, font_size)

        self.p_score: int = 0
        self.comp_score: int = 0

        # The position where the score should be displayed
        self.p_position: tuple = p_position
        self.comp_position: tuple = comp_position

        self.p_multiplier = 1
        self.comp_multiplier = 1

    def draw(self, screen: display) -> None:

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
