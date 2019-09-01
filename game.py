import collections
import random

from window import Window
from player import Player


class Game:
    def __init__(self, window: Window, player: Player):
        self._win = window
        self._player = player
        self._obstacles = []

    def setup(self):
        self._win.render_menu()
        for _ in range(4):
            self.add_obstacle((random.randint(0, 3), random.randint(0, 3)))
            self._win.draw_obstacles(self._obstacles)
            self._win.update()

    def step(self, action):
        lost = False
        self._win.draw_player(self._player)

    def add_obstacle(self, tile):
        self._obstacles.append(tile)
