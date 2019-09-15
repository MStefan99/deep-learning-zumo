from DQNAgent import DQNAgent
from player import Player
from window import Window
from game import Game

debug = False

window = Window(tile_size=30, width=7, height=11)
player = Player(window)
game = Game(window, player, verbose=debug)

# If skip_training value is true, a pre-made file with matching number of games will be automatically loaded,
# if present. Otherwise the default file with 100000 games will be loaded.
# You can see available values in the 'weights' folder.

skip_training = False
games_start = 340000
games_total = 400000
validation_games = 3000
validation_max_steps = 100
game_max_steps = 25


def main():
    game.setup()
    game.set_mode('random')
    if debug:
        game.play()

    agent = DQNAgent(game, skip_training)
    agent.train(games_start, games_total)
    agent.validate(games_total, validation_games, validation_max_steps)
    agent.play(games_total, game_max_steps)


if __name__ == '__main__':
    main()
