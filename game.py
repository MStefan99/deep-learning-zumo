import collections
import random

import pygame

from window import Window
from player import Player


class Game:
    def __init__(self, window: Window, player: Player):
        self._window = window
        self._player = player
        self._obstacles = []

    def reset(self):
        self._obstacles = []
        self._player.reset()

        self.setup()

    def setup(self):
        self._generate_obstacles(4)
        self._draw_ui()

    def step(self):
        crashed = False
        self._draw_ui()

        if self._crashed():
            crashed = True
            self.reset()

    def play(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    action = 0
                    if event.key == pygame.K_UP:
                        action = 0
                    if event.key == pygame.K_RIGHT:
                        action = 1
                    if event.key == pygame.K_DOWN:
                        action = 2
                    if event.key == pygame.K_LEFT:
                        action = 3
                    self._player.move(action)
                    self.step()

    def _crashed(self):
        coords = self._player.get_coords()
        if (coords[0] < 0 or coords[0] > self._window.get_dimensions()[0] - 1) \
                or (coords[1] < 0 or coords[1] > self._window.get_dimensions()[1] - 1) \
                or (coords in self._obstacles):
            return True
        else:
            return False

    def _generate_obstacles(self, count):
        for _ in range(count):
            x, y = random.randint(1, 6), random.randint(2, 8)
            self._add_obstacle((x, y))
            direction = random.randint(0, 3)
            if direction == 0:
                y = y - 1
            if direction == 1:
                x = x + 1
            if direction == 2:
                y = y + 1
            if direction == 3:
                x = x - 1
            self._add_obstacle((x, y))

    def _add_obstacle(self, tile):
        self._obstacles.append(tile)

    def _get_obstacles(self):
        return self._obstacles

    def _draw_ui(self):
        self._window.clear()
        self._window.render_menu()
        self._window.draw_obstacles(self._obstacles)
        self._window.draw_player(self._player)
        self._window.draw_finish()
        self._window.update()
