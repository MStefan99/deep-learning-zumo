import paho.mqtt.client as mqtt
from DQNAgent import DQNAgent


class Server:
    def __init__(self, host, game, player):
        self._client = mqtt.Client()
        self._game = game
        self._player = player
        self._agent = DQNAgent(game, True)
        self._observation = self._game.reset()
        self._done = False
        self._repeated_actions = 0
        self._history = []

        self._client.connect(host)
        self._client.subscribe('Zumo/#', 0)
        self._client.on_message = self.on_message

    def play(self, model_games):
        self._agent.load_model(model_games, True)

        self._client.publish('Net/Status', 'Ready')
        self._client.loop_forever()

    def on_message(self, client, obj, msg):
        if 'Start' in msg.topic:
            self._game.reset()
            self._player.reset()
            self._history = []
            self._observation = self._game.observe()
            action = self._agent.predict(self._observation)
            self._client.publish('Net/Action', int(action))

        elif 'Coords' in msg.topic:
            coords = self._player.get_coords()
            self._client.publish('Net/Coords', f'{coords}')

        elif 'Move' in msg.topic:
            if not self._done and (b'ok' in msg.payload):
                self._observation = self._game.observe()
                action = self._agent.predict(self._observation)
                _, _, self._done, _ = self._game.step(action)
                if self._player.get_coords() in self._history:
                    self._repeated_actions += 1
                    if self._repeated_actions > 5:
                        self._client.publish('Net/Status', 'Stuck')
                        self._client.disconnect()
                self._history.append(self._player.get_coords())

                self._client.publish('Net/Action', int(action))
            if self._done:
                self._client.publish('Net/Status', 'Finish')
                self._client.disconnect()

        elif 'Obst' in msg.topic:
            string = msg.payload.decode('utf-8')
            obstacle = tuple(map(int, string[1:-1].split(", ", 1)))
            self._game.add_obstacle(obstacle)
            self._client.publish('Net/Status', f'Obst ok {obstacle}')
