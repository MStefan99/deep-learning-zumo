from DQNAgent import DQNAgent
from player import Player
from window import Window
from game import Game
from mqtt import Server

debug = False
mqtt = True
skip_setup = True
skip_training = True


window = Window(tile_size=30, width=7, height=11)
player = Player(window)
game = Game(window, player, verbose=debug)

# If skip_training value is true, a pre-made file with matching number of games will be automatically loaded,
# if present. Otherwise the default file with 10 million games will be loaded.
# You can see available values in the 'weights' folder.

games_start = 0
games_total = 10**7
validation_games = 3000
validation_max_steps = 100
game_max_steps = 25


def main():
    game.set_mode('manual')
    game.setup(skip_setup)

    if debug:
        game.play()

    if mqtt:
        server = Server("127.0.0.1", game, player, verbose=True)
        server.play(games_total)
    else:
        game.set_mode('random')
        agent = DQNAgent(game, skip_training)
        agent.train(games_start, games_total)
        agent.validate(games_total, validation_games, validation_max_steps)
        agent.play(games_total, game_max_steps)


if __name__ == '__main__':
    main()
