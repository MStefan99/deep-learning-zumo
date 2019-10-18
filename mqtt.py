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
        self._zumo_ready = False
        self._repeated_actions = 0
        self._history = []

        self._client.connect(host)
        self._client.subscribe('Zumo/#', 0)
        self._client.on_message = self.on_message

    def play(self, model_games):
        self._agent.load_model(model_games, True)

        print('Sending ready status')
        self._client.publish('Net/Status', 'Ready')
        self._client.publish('Info/Net', f'Loaded model trained on {model_games} games')
        self._client.loop_forever()

    def on_message(self, client, obj, msg):
        self._client.publish('Rec/Net', f'Rec on "{msg.topic}"')

        if 'Status' in msg.topic:
            if b'Boot' in msg.payload:
                print('Received robot boot confirmation')
                self._client.publish('Ack/Net', 'Boot')
                self._client.publish('Net/Status', 'Ready')
                print('Sending ready status')

            if b'Ready' in msg.payload:
                print('\nReceived robot ready confirmation')
                self._client.publish('Ack/Net', 'Ready')
                if not self._zumo_ready:
                    self._observation = self._game.observe()
                    action = self._agent.predict(self._observation)
                    self._client.publish('Net/Action', int(action))
                    print('Sending first action order')
                else:
                    print('Already sent first action order, skipping')
                self._zumo_ready = True

        elif 'Coords' in msg.topic:
            print('Received current robot state')
            string = msg.payload.decode('utf-8')
            coords = tuple(map(int, string[1:-1].split(", ", 1)))
            self._player.set_coords(coords)
            self._client.publish('Ack/Net', f'Coords {coords} set')

        elif 'Request' in msg.topic:
            if b'Coords' in msg.topic:
                print('Received request of current coordinates')
                self._client.publish('Ack/Net', 'Coords')
                coords = self._player.get_coords()
                self._client.publish('Net/Coords', f'{coords}')
                print('Sending coordinates')

        elif 'Move' in msg.topic:
            print('Received move confirmation')
            self._client.publish('Ack/Net', 'Move')
            if not self._done:
                action = int(msg.payload.decode('utf-8'))
                _, _, self._done, _ = self._game.step(action)
                self._observation = self._game.observe()
                action = self._agent.predict(self._observation)

                if self._player.get_coords() in self._history:
                    self._repeated_actions += 1
                    self._client.publish('Info/Net',
                                         f'Repeated actions: {self._repeated_actions}')
                    if self._repeated_actions > 5:
                        self._client.publish('Net/Status', 'Stuck')
                        print('Agent stuck. Sending stuck signal')
                        self._client.disconnect()

                if not self._done:
                    self._history.append(self._player.get_coords())
                    self._client.publish('Net/Action', int(action))
                    print('Sending next action order')

            if self._done:
                print('Game complete. Sending finish status')
                self._client.publish('Net/Status', 'Finish')
                self._client.disconnect()

        elif 'Obst' in msg.topic:
            print('Received obstacle info')
            string = msg.payload.decode('utf-8')
            obstacle = tuple(map(int, string[1:-1].split(", ", 1)))
            self._game.smart_add(obstacle)
            self._client.publish('Ack/Net', f'Obst {obstacle}')
            print(f'Sending obstacle {obstacle} acknowledgement')
