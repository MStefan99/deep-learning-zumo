import pygame
from window import Window


class Player:
    def __init__(self, window: Window):
        self._window = window
        pygame.init()
        pygame.display.set_caption("THE GAME!")
        self._x, self._y = 0, 0
        self._action = 0
        size = self._window.get_size()
        self._prev_pos = [(size[0] // 2, size[1] - 1)] * 5

        self.reset()

    def reset(self):
        size = self._window.get_size()
        pos = size[0] // 2, size[1] - 1
        self._x, self._y = pos
        self._prev_pos = [pos, self._prev_pos[0]]

    def get_coords(self):
        return self._x, self._y

    def set_coords(self, tile):  # Required for mqtt
        self._x, self._y = tile

    def move(self, action):
        self._action = action
        self._prev_pos = [self.get_coords(), self._prev_pos[0]]
        if action == 0:
            self._y = self._y - 1
        if action == 1:
            self._x = self._x + 1
        if action == 2:
            self._y = self._y + 1
        if action == 3:
            self._x = self._x - 1

    def get_last_action(self):
        return self._action

    def get_prev_pos(self):
        return self._prev_pos
