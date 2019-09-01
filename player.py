import pygame
import colors as color
from window import Window


class Player:
    def __init__(self, window: Window):
        self._window = window
        pygame.init()
        pygame.display.set_caption("THE GAME!")
        self._x, self._y = 0, 0

        self.reset()

    def reset(self):
        size = self._window.get_dimensions()
        self._x, self._y = size[0] // 2, size[1] - 1

    def get_coords(self):
        return self._x, self._y

    def move(self, action):
        if action == 0:
            self._y = self._y - 1
        if action == 1:
            self._x = self._x + 1
        if action == 2:
            self._y = self._y + 1
        if action == 3:
            self._x = self._x - 1
