import asyncio
import os
import pickle

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
        self.crypto = NQCryptoClient()

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
            trans, proto = await loop.create_connection(factory,
                    self.config.get('client_address'),
                    self.config.get('client_port'))

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

                print('Secure channel established')

                data['handshake'] = False
                data['salt'] = None
            
            message = data.get('message')
            if type(message) is bytes:
                message = self.crypto.decrypt(message)
            #print(message)

            # maybe there are some errors to display
            errors = message.get('errors')
            if type(errors) is list and len(errors):
                for e in errors:
                    print(f'error: {e}')

            result = message.get('result')
            if type(result) is dict and len(result):
                # todo: result renderers
                print(result)

            query = input(f'({message.get("section")})> ')

            message['query'] = query
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

