from DQNAgent import DQNAgent
from player import Player
from window import Window
from game import Game

window = Window(tile_size=30, width=7, height=10)
player = Player(window)
game = Game(window, player)


# If skip_training value is true, a pre-made file with matching number of games will be automatically loaded,
# if present. Otherwise the default file with 5000 games will be loaded.
# You can see available values in the 'weights' folder.

skip_training = True
games_number = 5000


# If the snake gets to run in a loop, just click anywhere in the game window with a mouse.


def main():
    game.setup()
    while True:
        pass


if __name__ == '__main__':
    main()
