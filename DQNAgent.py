import os
import random
from time import time

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from game import Game

from log import log_process

file_prefix = 'weights/weights_'
default_games = 10**7
files = 5
debug = False


class DQNAgent:
    def __init__(self, game: Game, skip_training=False):
        self._gamma = 0.95
        self._epsilon_start = 1.0
        self._epsilon = self._epsilon_start
        self._epsilon_min = 0.1
        self._learning_rate = 0.0005
        self._skip_training = skip_training

        self._game = game
        self._input_nodes = len(self._game.reset())
        self._output_nodes = 4
        self._model = self._build_model(self._input_nodes,
                                        self._output_nodes)

    def train(self, start_games, model_games):
        if not self._skip_training:
            print(f'=== TRAINING START ===')
            if model_games < start_games:
                print(f'Total number of games is smaller than the starting number. '
                      f'Loading model trained on {start_games} games.')
            elif self.load_model(start_games, False):
                print(f'Continuing to train up to {model_games} games.')
            else:
                print(f'Starting to train model on {model_games} games.')
                start_games = 0

            start = time()
            self._game.set_window_mode('Train')

            for game in range(start_games, model_games):
                won = False
                steps = 0
                reward_total = 0
                done = False
                training_data = []
                prev_observation = observation = self._game.reset()

                if self._epsilon > self._epsilon_min:
                    self._epsilon = self._epsilon_start * (1 - game / model_games)

                while not done:
                    if random.uniform(0, 1) < self._epsilon:
                        action = random.randrange(0, self._output_nodes)
                    else:
                        action = np.argmax(self._model.predict(np.array(observation).reshape([-1, self._input_nodes])))
                    observation, reward, done, info = self._game.step(action)

                    training_data.append([prev_observation, action, reward, observation, done])
                    prev_observation = observation

                    if info['won']:
                        won = True
                    reward_total += reward
                    steps += 1

                self._replay(training_data)
                if game % ((model_games - start_games) // files) == (model_games - start_games) // files - 1:
                    self._model.save_weights(f'{file_prefix}{game + 1}', overwrite=True)

                if debug:
                    print(f'Game {game} finished. {"Won" if won else "Lost"} in {steps} steps, ' +
                          f'eps: {round(self._epsilon, 2)}')
                else:
                    log_process('Training, please wait...', game - start_games + 1, model_games - start_games, 50,
                                time_start=start, time_now=time(), accuracy=2, time_correction=2,
                                info=f'{"Won" if won else "Lost"} in {steps} steps, '
                                     f'Avg reward: {round(reward_total / game, 3) if game > 0 else 0}, '
                                     f'Epsilon: {round(self._epsilon, 2)}.')
            print(f'Trained model on {model_games - start_games if model_games > start_games else 0} games.')
            print(f'=== TRAINING END ===')

    def _replay(self, training_data):
        for prev_state, action, reward, state, done in training_data:
            prev_state = np.reshape(prev_state, [1, self._input_nodes])
            state = np.reshape(state, [1, self._input_nodes])

            target = reward
            if not done:
                target = (reward + self._gamma *
                          np.amax(self._model.predict(state)[0]))
            target_f = self._model.predict(prev_state)
            target_f[0][action] = target
            self._model.fit(prev_state, target_f, epochs=1, verbose=0)

    def _build_model(self, in_size, out_size):
        model = Sequential()
        model.add(Dense(16, input_dim=in_size, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(out_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self._learning_rate))

        return model

    def load_model(self, model_games, load_default=True):
        if os.path.isfile(f'{file_prefix}{model_games}'):
            self._model.load_weights(f'{file_prefix}{model_games}')
            print(f'Model trained on {model_games} games successfully loaded.')
            return True
        elif os.path.isfile(f'{file_prefix}{default_games}'):
            if load_default:
                print(f'Warning, no model trained on {model_games} games found! ' 
                      f'Loading default model trained on {default_games} games.')
                self._model.load_weights(f'{file_prefix}{default_games}')
                return True
            else:
                print(f'Warning, no model trained on {model_games} games found! '
                      f'Default model won\'t be loaded. '
                      f'Starting with a new model!')
                return False
        else:
            print(f'Warning, no model trained on {model_games} games and default is unavailable! '
                  f'Starting with a new model!')
            return False

    def play(self, model_games, max_steps):
        print(f'=== GAME START ===')
        print(f'Starting the game with model trained on {model_games} games with {max_steps} maximum steps.')
        self._game.set_window_mode('Visual')
        game = 0
        self.load_model(model_games)

        while True:
            observation = self._game.reset()
            won = False
            steps = 0

            for step in range(max_steps):
                action = np.argmax(self._model.predict(np.array(observation).reshape([-1, self._input_nodes])))
                observation, reward, done, info = self._game.step(action)

                if info['won']:
                    won = True
                if done:
                    print(f'Game {game + 1} finished. {"Won" if won else "Lost"} in {steps + 1} steps.')
                    break
                if step == max_steps - 1 and not done:
                    print(f'Game {game + 1} finished. Number of allowed steps exceeded.')

                self._game.delay()
                steps += 1
            game += 1

    def validate(self, model_games, validation_games, max_steps):
        print(f'=== VALIDATION START ===')
        print(f'Starting to validate model trained on {validation_games} games with {max_steps} maximum steps.')
        games_won = 0
        self.load_model(model_games)
        start_time = time()
        self._game.set_window_mode('Train')

        for game in range(validation_games):
            observation = self._game.reset()

            for step in range(max_steps):
                action = np.argmax(self._model.predict(np.array(observation).reshape([-1, self._input_nodes])))
                observation, reward, done, info = self._game.step(action)

                if info['won']:
                    games_won += 1
                if done:
                    break

            log_process('Validating...', game + 1, validation_games, 50,
                        time_start=start_time, time_now=time(),
                        info=f'Current score: {round(100 * games_won / (game + 1) , 2)}%.')

        print(f'Validation finished. Final score: {round(100 * games_won / validation_games, 4)}%.')
        print(f'=== VALIDATION END ===')

    def predict(self, observation):
        action = np.argmax(self._model.predict(np.array(observation).reshape([-1, self._input_nodes])))
        return action
