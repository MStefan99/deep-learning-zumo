import paho.mqtt.client as mqtt
from DQNAgent import DQNAgent


class Server:
    def __init__(self, host, game, player, verbose=False):
        self._client = mqtt.Client()
        self._game = game
        self._player = player
        self._verbose = verbose
        self._agent = DQNAgent(game, True)
        self._observation = self._game.reset()
        self._done = False
        self._repeated_actions = 0
        self._steps = 0
        self._version = 'v0.1'

        self._client.connect(host)
        self._client.subscribe('Zumo/#', 0)
        self._client.on_message = self.on_message

    def play(self, model_games):
        self._agent.load_model(model_games, True)

        print('Sending ready status')
        self._client.publish('Net/Status', 'Ready')
        self._client.publish('Info/Net/Load', f'Loaded model trained on {model_games} games')
        self._client.loop_forever()

    def on_message(self, client, obj, msg):
        self._client.publish('Rec/Net', f'Rec on "{msg.topic}"')

        if 'Zumo/Status' == msg.topic:
            if b'Ready' == msg.payload:
                self._observation = self._game.reset()
                self._done = False
                self._steps = 0
                self._repeated_actions = 0
                print('\nReceived robot ready confirmation, new game started')
                self._client.publish('Ack/Net', 'Ready')
                self._client.publish('Net/Status', 'Ready')

        elif 'Zumo/Version' == msg.topic:
            self._client.publish('Ack/Net', 'Version')
            self._client.publish('Net/Version', self._version)
            version = msg.payload.decode('utf-8')
            if self._version == version:
                print(f'Found Zumo, version {version}')
            else:
                print(f'Zumo version mismatch: expected {self._version}, found {version}')
                print('Stopping server to prevent conflicts')
                self._client.publish('Info/Net/WARNING', 'Incompatible')
                self._client.disconnect()

        elif 'Zumo/Coords' == msg.topic:
            string = msg.payload.decode('utf-8')
            coords = tuple(map(int, string[1:-1].split(", ", 1)))
            if self._verbose:
                print(f'Received current robot coordinates: {coords}')
            else:
                print('Received current robot coords')
            self._player.set_coords(coords)
            self._client.publish('Ack/Net', f'Coords {coords} set')

        elif 'Zumo/Request' == msg.topic:
            if b'Coords' == msg.topic:
                print('Received request of current coordinates')
                self._client.publish('Ack/Net', 'Coords')
                coords = self._player.get_coords()
                self._client.publish('Net/Coords', f'{coords}')
                if self._verbose:
                    print(f'Sending current player coordinates: {coords}')
                else:
                    print('Sending coordinates')

        elif 'Zumo/Move' == msg.topic:
            self._client.publish('Ack/Net', 'Move')
            move = int(msg.payload.decode('utf-8'))
            if self._verbose:
                print(f'Received confirmation of move {move}')
            else:
                print('Received move confirmation')
            _, _, self._done, _ = self._game.step(move)
            self._observation = self._game.observe()
            action = self._agent.predict(self._observation)

            if 0 <= move <= 3:
                self._steps += 1

            if self._player.get_coords() in self._player.get_history() and 0 <= move <= 3:
                self._repeated_actions += 1
                if self._verbose:
                    print(f'Repeated action {self._repeated_actions} time(s)')
                self._client.publish('Info/Net/RA',
                                     f'Repeated actions: {self._repeated_actions}')
                if self._repeated_actions > 5:
                    self._client.publish('Net/Status', 'Stuck')
                    if self._verbose:
                        print(f'Repeated action {self._repeated_actions} time(s). '
                              f'Sending stuck signal')
                    else:
                        print('Agent stuck. Sending stuck signal')
                    self._client.publish('Info/Net/Status', f'Network stuck after '
                                                            f'{self._steps - self._repeated_actions} steps')
                    self._client.disconnect()

            if not self._done:
                self._client.publish('Net/Action', int(action))
                if self._verbose:
                    print(f'Sending an order to execute action {action}')
                else:
                    print('Sending next action order')

            if self._done:
                print('Game complete. Sending finish status')
                self._client.publish('Net/Status', 'Finish')
                self._client.publish('Info/Net/Status', f'Game finished after {self._steps} step(s), '
                                                        f'{self._repeated_actions} repeated')
                self._client.disconnect()

        elif 'Zumo/Obst' == msg.topic:
            string = msg.payload.decode('utf-8')
            obstacle = tuple(map(int, string[1:-1].split(", ", 1)))
            self._game.smart_add(obstacle)
            self._client.publish('Ack/Net', f'Obst {obstacle}')
            if self._verbose:
                print(f'Received obstacle {obstacle} info')
            else:
                print('Received obstacle info')
