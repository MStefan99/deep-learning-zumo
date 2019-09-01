import os
import random
from time import time

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from log import log_process

file_prefix = 'weights/weights_'
default_games = 5000
files = 10
debug = False


class DQNAgent:
    def __init__(self, window, snake, games_number, skip_training=False):
        self._gamma = 0.95
        self._epsilon_start = 1.0
        self._epsilon = self._epsilon_start
        self._epsilon_min = 0.1
        self._learning_rate = 0.0005
        self._games_number = games_number
        self._skip_training = skip_training

        self._window = window
        self._snake = snake
        self._input_nodes = len(self._snake.reset())
        self._output_nodes = 4
        self._model = self.build_model(self._input_nodes,
                                       self._output_nodes)

    def train(self, games):
        if not self._skip_training:
            start = time()

            for game in range(games):
                score = 0
                steps = 0
                reward_total = 0
                done = False
                training_data = []
                prev_observation = observation = self._snake.reset()
                self._window.generate_food_for_snake(self._snake.get_snake())

                if self._epsilon > self._epsilon_min:
                    self._epsilon = self._epsilon_start * (1 - game / games)

                while not done:
                    if random.uniform(0, 1) < self._epsilon:
                        action = random.randrange(0, self._output_nodes)
                    else:
                        action = np.argmax(self._model.predict(np.array(observation).reshape([-1, self._input_nodes])))
                    observation, reward, done, info = self._snake.step(action)

                    training_data.append([prev_observation, action, reward, observation, done])
                    prev_observation = observation

                    if info['Eaten']:
                        score += 1
                    reward_total += reward
                    steps += 1

                if not debug:
                    log_process('Training, please wait...', game, games, 50,
                                time_start=start, time_now=time(), time_correction=2,
                                info=f'Score: {score} in {steps} steps, '
                                f'Avg reward: {round(reward_total / game, 2) if game > 0 else 0}, '
                                f'Epsilon: {round(self._epsilon, 2)}.')

                self.replay(training_data)

                if game % (games // files) == games // files - 1:
                    self._model.save_weights(f'{file_prefix}{game + 1}', overwrite=True)

                if debug:
                    print(f'Game {game} finished. Score: {round(score, 2)} in {steps} steps, ' +
                          f'eps: {round(self._epsilon, 2)}')

    def replay(self, training_data):
        for prev_state, action, reward, state, done in training_data:
            prev_state = np.reshape(prev_state, [1, self._input_nodes])
            state = np.reshape(prev_state, [1, self._input_nodes])

            target = reward
            if not done:
                target = (reward + self._gamma *
                          np.amax(self._model.predict(state)[0]))
            target_f = self._model.predict(prev_state)
            target_f[0][action] = target
            self._model.fit(prev_state, target_f, epochs=1, verbose=0)

    def build_model(self, in_size, out_size):
        model = Sequential()
        model.add(Dense(64, input_dim=in_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(out_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self._learning_rate))

        return model

    def play(self):
        game = 0

        if self._skip_training:
            if os.path.isfile(f'{file_prefix}{self._games_number}'):
                self._model.load_weights(f'{file_prefix}{self._games_number}')
                print(f'Model trained on {self._games_number} games successfully loaded')
            elif os.path.isfile(f'{file_prefix}{default_games}'):
                print(f'Warning, no model file found! Playing game with default model trained on {default_games} games')
                self._model.load_weights(f'{file_prefix}{default_games}')
            else:
                print('Warning, no model file found and default is unavailable! Playing with random model!')

        while True:
            observation = self._snake.reset()
            self._window.generate_food_for_snake(self._snake.get_snake())
            score = 0
            steps = 0
            done = False

            while not done:
                action = np.argmax(self._model.predict(np.array(observation).reshape([-1, self._input_nodes])))
                observation, reward, done, info = self._snake.step(action)

                if info['Eaten']:
                    score += 1

                self._window.update()
                self._window.delay()
                self._window.clear()
                steps += 1

            game += 1
            print(f'Game {game} finished. Score: {round(score, 2)} in {steps} steps.')
