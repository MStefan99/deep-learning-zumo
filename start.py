from DQNAgent import DQNAgent
from player import Player
from window import Window
from game import Game
from mqtt import Server

debug = False

window = Window(tile_size=30, width=7, height=11)
player = Player(window)
game = Game(window, player, verbose=debug)

# If skip_training value is true, a pre-made file with matching number of games will be automatically loaded,
# if present. Otherwise the default file with 10 million games will be loaded.
# You can see available values in the 'weights' folder.

skip_training = True
games_start = 0
games_total = 10**7
validation_games = 3000
validation_max_steps = 100
game_max_steps = 25


def main():
    game.set_mode('manual')
    if debug:
        game.play()

    server = Server("192.168.1.8", game, player)
    server.play(games_total)


if __name__ == '__main__':
    main()
