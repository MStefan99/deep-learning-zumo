import pygame
import colors as color


class Player:
    def __init__(self, window):
        self._window = window
        pygame.init()
        pygame.display.set_caption("ASDAAJLDK")

        self._x, self._y = 0, 0
        self.color = color.red

    def get_coords(self):
        return self._x, self._y
