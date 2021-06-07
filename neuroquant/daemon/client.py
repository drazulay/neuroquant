import asyncio
import os
import pickle
import readline

from ..crypto import NQCryptoClient



"""
NQClient

Implements asyncio client

args:
    config: NQConfig object

"""
class NQClient(object):

    def __init__(self, config):
        self.config = config
        self.crypto = NQCryptoClient(config)
        self.host = config.get('host_address')
        self.port = config.get('host_port')

        self.commands = []

        readline.parse_and_bind('tab: complete')
        readline.set_completer(self._complete)

    def _complete(self, text, state):
        for command in self.commands:
            if command.startswith(text):
                if state:
                    state -=1
                else:
                    return command

    """
    Async event loop
    """
    async def main(self):
        factory = lambda: NQClientProto(data, future)
        loop = asyncio.get_running_loop()

        message = {"query": None,
                   "errors": None,
                   "result": None,
                   "section": 'nq',}

        data = {"handshake": True,
                "message": message,
                "pubkey": self.crypto.get_public_key(),
                "salt": os.urandom(16),
                "stop": False,}

        while True:
            future = loop.create_future()

            # wait for connection
            trans, proto = await loop.create_connection(factory, self.host,
                    self.port)

            # wait for data from server
            await future

            data = pickle.loads(future.result())
            #print(f'DATA: {data}')

            # stop querying the server plz
            if data.get('stop'):
                print('Stop signal received from server')
                break

            # finish handshake
            if data.get('handshake'):
                data["pubkey"] = self.crypto.associate(
                        data.get('pubkey'),
                        data.get('salt'))

                print(f'Secure channel established to {self.host}:{self.port}')

                data['handshake'] = False
                data['salt'] = None
                # Needed to fill tab-complete help
                data['message'] = {"section": "nq", "query": "help"}
                continue

            message = data.get('message')
            if type(message) is bytes:
                message = self.crypto.decrypt(message)

            query = message.get('query')
            if type(query) is list and len(query):
                print(query)

            # maybe there are some errors to display
            errors = message.get('errors')
            if type(errors) is list and len(errors):
                for e in errors:
                    print(f'error: {e}')

            commands = message.get('commands')
            if type(commands) is list and len(commands):
                self.commands = commands

            result = message.get('result')
            if type(result) is dict and len(result):
                if "quit" in result:
                    break
                # save X25519 keys for reuse
                elif "save_client_keys" in result:
                    self.config.write('auth', self.crypto.save_keys())
                else:
                    print(result)
            
            section = message.get('section')
            try:
                query = input(f'({message.get("section")})> ')
                message['query'] = query
            except EOFError:
                if section == 'nq':
                    print ('Gracefully exiting..')
                    message['query'] = 'quit'
                else:
                    print ("\n")
                    message['query'] = 'back'

            message["result"] = None

            data["message"] = self.crypto.encrypt(message)

        print('Goodbye.')

    """
    Start responding to messages

    todo:
        - compression
        - identify as user or as bot, each gets different sets of commands
    """
    def start(self):
        asyncio.run(self.main())


"""
NQClientProto

Implements asyncio client protocol handler

args:
    - data: bytes-like data to be sent
      structure:

      {
        "commands": [...],      -> list of available commands for section
        "query": ["help"],      -> last entered query
        "result": {...},        -> result of last entered query
        "prompt": "(algo)> ",   -> prompt to show user
        "section": "algo",      -> currently active section
      } 

    - future: Future instance
"""
class NQClientProto(asyncio.Protocol):

    def __init__(self, data, future):
        self.data = data
        self.future = future

    """
    Callback triggered data is received
    """
    def data_received(self, data):
        self.future.set_result(data)

    """
    Callback triggered when a connection is established
    """
    def connection_made(self, transport):
        self.transport = transport
        transport.write(pickle.dumps(self.data))

    """
    Callback triggered when a connection is lost
    """
    def connection_lost(self, exc):
        self.transport.close()

