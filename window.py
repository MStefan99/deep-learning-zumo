import pygame
import colors as color


class Window:
    def __init__(self, tile_size, width, height, speed=20, mode='Visual'):
        self._tiles_horizontal = width
        self._tiles_vertical = height
        self._vertical_buffer = tile_size
        self._win_width = width * tile_size
        self._win_height = height * tile_size
        self._tile_height = self._win_height / self._tiles_vertical
        self._tile_width = self._win_width / self._tiles_horizontal

        self._speed = speed
        self._mode = mode
        self._window = pygame.display.set_mode((self._win_width, self._win_height + self._vertical_buffer))

        pygame.font.init()
        self._font = pygame.font.SysFont('Consolas', tile_size // 2)

    def render_menu(self):
        pygame.draw.rect(self._window, color.grey,
                         (0, 0, self._win_width / 2, self._tile_height), 10)

    def set_mode(self, mode):
        if mode == 'Visual':
            self._mode = 'Visual'
        elif mode == 'Train':
            self._mode = 'Train'

    def update(self):
        if self._mode == 'Visual':
            pygame.display.update()

    def clear(self):
        if self._mode == 'Visual':
            self._window.fill((0, 0, 0))

    def get_dimensions(self):
        return self._tiles_horizontal, self._tiles_vertical

    def set_speed(self, speed):

        if 0 <= speed <= 1000:
            self._speed = speed

    def tile_to_window_coords(self, tile):
        return tile[0] * self._tile_width, tile[1] * self._tile_height + self._vertical_buffer

    def window_coords_to_tile(self, coords):
        tile = coords[0] / self._tile_width, coords[1] - self._vertical_buffer / self._tile_height
        return tile

    def draw_player(self, player):
        x, y = self.tile_to_window_coords(player.get_coords())
        pygame.draw.rect(self._window, color.green, (x, y, self._tile_width, self._tile_height))

    def draw_obstacles(self, obstacles):
        for obstacle in obstacles:
            x, y = self.tile_to_window_coords(obstacle)
            pygame.draw.rect(self._window, color.red, (x, y, self._tile_width, self._tile_height))

    def draw_finish(self):
        for i in range(self._tiles_horizontal):
            x, y = self.tile_to_window_coords((i, 0))
            pygame.draw.rect(self._window, color.dark_blue, (x, y, self._tile_width, self._tile_height))
