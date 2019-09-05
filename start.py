from DQNAgent import DQNAgent
from player import Player
from window import Window
from game import Game

window = Window(tile_size=30, width=7, height=11)
player = Player(window)
game = Game(window, player, verbose=False)


# If skip_training value is true, a pre-made file with matching number of games will be automatically loaded,
# if present. Otherwise the default file with 5000 games will be loaded.
# You can see available values in the 'weights' folder.

skip_training = False
games_number = 5000
validation_games = 1000
validation_max_steps = 25

# If the snake gets to run in a loop, just click anywhere in the game window with a mouse.


def main():
    game.setup()

    game.set_mode('random')

    agent = DQNAgent(game, games_number, skip_training)
    agent.train(games_number)
    agent.validate(validation_games, validation_max_steps)
    # game.set_mode('manual')
    agent.play()


if __name__ == '__main__':
    main()
