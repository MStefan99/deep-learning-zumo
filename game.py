import random
import pygame
from window import Window
from player import Player


class Game:
    def __init__(self, window: Window, player: Player, verbose=False):
        self._window = window
        self._player = player
        self._obstacles = []
        self._verbose = verbose

    def reset(self):
        self._obstacles = []
        self._player.reset()

        self.setup()
        return self._observe()

    def setup(self):
        self._generate_obstacles(4)
        self._draw_ui()
        # TODO: Interactive GUI for setting obstacles

    def step(self, action):
        info = {}
        self._player.move(action)
        done = self._done()
        self._draw_ui()

        info['won'] = self._won()
        info['coords'] = self._player.get_coords()
        observation = self._observe()
        reward = self._get_reward()

        if self._verbose:
            print(f'Observation: {observation}, reward: {reward}, done: {done}, info: {info}')

        if self._done() or self._won():
            self.reset()
        return observation, reward, done, info

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
                    self.step(action)

    def delay(self, delay):
        self._window.delay(delay)

    def set_window_mode(self, mode):
        self._window.set_mode(mode)

    def _done(self):
        coords = self._player.get_coords()
        if (coords[0] < 0 or coords[0] > self._window.get_dimensions()[0] - 1) \
                or (coords[1] < 1 or coords[1] > self._window.get_dimensions()[1] - 1) \
                or (coords in self._obstacles):
            return True
        else:
            return False

    def _won(self):
        if self._player.get_coords()[1] == 0:
            return True
        else:
            return False

    def _generate_obstacles(self, count):
        for _ in range(count):
            x, y = random.randint(1, 5), random.randint(3, 8)
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

    def _get_reward(self):
        lost = self._done()
        won = self._won()
        last_action = self._player.get_last_action()

        if won:
            return 5
        elif lost:
            return -1
        elif last_action == 0:
            return 0.1
        elif last_action == 2:
            return -0.3
        else:
            return -0.1

    def _observe(self):
        observation = self._obstacle_next()

        return observation

    def _obstacle_next(self):
        data = [0] * 4
        coords = self._player.get_coords()

        if self._is_obstacle((coords[0], coords[1] - 1)):
            data[0] = 1
        if self._is_obstacle((coords[0] + 1, coords[1])):
            data[1] = 1
        if self._is_obstacle((coords[0], coords[1] + 1)):
            data[2] = 1
        if self._is_obstacle((coords[0] - 1, coords[1])):
            data[3] = 1
        return data

    def _is_obstacle(self, tile):
        if (tile[0] < 0 or tile[0] > self._window.get_dimensions()[0] - 1) \
                or (tile[1] < 0 or tile[1] > self._window.get_dimensions()[1] - 1) \
                or tile in self._obstacles:
            return True
        else:
            return False

    def _draw_ui(self):
        self._window.clear()
        self._window.render_menu()
        self._window.draw_obstacles(self._obstacles)
        self._window.draw_player(self._player)
        self._window.draw_finish()
        self._window.update()

    def get_window(self):
        return self._window

    def get_player(self):
        return self._player
