import pygame
import colors as color


class Window:
    def __init__(self, tile_size, width, height, speed=10, mode='Visual'):
        self._tiles_horizontal = width
        self._tiles_vertical = height
        self._vertical_buffer = tile_size
        self._win_width = width * tile_size
        self._win_height = height * tile_size
        self._tile_height = self._win_height // self._tiles_vertical
        self._tile_width = self._win_width // self._tiles_horizontal

        self._speed = speed
        self._mode = mode
        self._state = 'Setup'
        self._surface = pygame.display.set_mode((self._win_width, self._win_height + self._vertical_buffer))

        pygame.font.init()
        self._font = pygame.font.SysFont('consolas', tile_size // 2)

    def render_menu(self):
        button1_color = color.green
        button2_color = color.red

        if self._state == 'Setup':
            button1_text = self._font.render('Start', False, button1_color, color.black)
        else:
            button1_text = self._font.render('Setup', False, button1_color, color.black)
        text1_rect = button1_text.get_rect()
        text1_rect.center = (self._win_width // 4, self._tile_height // 2)
        self._surface.blit(button1_text, text1_rect)

        button2_text = self._font.render('Reset', False, button2_color, color.black)
        text2_rect = button2_text.get_rect()
        text2_rect.center = (3 * self._win_width // 4, self._tile_height // 2)
        self._surface.blit(button2_text, text2_rect)

        pygame.draw.rect(self._surface, button1_color,
                         (0, 0, self._win_width // 2, self._tile_height), 10)
        pygame.draw.rect(self._surface, button2_color,
                         (self._win_width // 2, 0, self._win_width // 2, self._tile_height), 10)

    def set_mode(self, mode):
        if mode == 'Visual' or mode == 'Train':
            self._mode = mode

    def set_state(self, state):
        if state == 'Setup' or state == 'Run':
            self._state = state

    def update(self):
        if self._mode == 'Visual':
            pygame.display.update()

    def clear(self):
        if self._mode == 'Visual':
            self._surface.fill((0, 0, 0))

    def delay(self):
        if self._mode == 'Visual':
            pygame.time.delay(1000 // self._speed)

    def get_dimensions(self):
        return self._win_width, self._win_height

    def get_tile_dimensions(self):
        return self._tile_width, self._tile_height

    def get_size(self):
        return self._tiles_horizontal, self._tiles_vertical

    def set_speed(self, speed):
        if 0 <= speed <= 1000:
            self._speed = speed

    def tile_to_window_coords(self, tile):
        return tile[0] * self._tile_width, tile[1] * self._tile_height + self._vertical_buffer

    def window_coords_to_tile(self, coords):
        tile = coords[0] // self._tile_width, (coords[1] - self._vertical_buffer) // self._tile_height
        return tile

    def draw_player(self, player):
        x, y = self.tile_to_window_coords(player.get_coords())
        pygame.draw.rect(self._surface, color.green, (x, y, self._tile_width, self._tile_height))

    def draw_obstacles(self, obstacles):
        for obstacle in obstacles:
            x, y = self.tile_to_window_coords(obstacle)
            pygame.draw.rect(self._surface, color.red, (x, y, self._tile_width, self._tile_height))

    def draw_finish(self):
        for i in range(self._tiles_horizontal):
            x, y = self.tile_to_window_coords((i, 0))
            pygame.draw.rect(self._surface, color.dark_blue, (x, y, self._tile_width, self._tile_height))
