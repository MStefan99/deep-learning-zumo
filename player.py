import pygame

green = (0, 255, 0)
red = (255, 0, 0)


class Player:
    def __init__(self, window):
        self._window = window
        pygame.init()
        pygame.display.set_caption("ASDAAJLDK")

        x, y = 0, 0
        self.color = red



