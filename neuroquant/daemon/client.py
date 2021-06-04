import asyncio
import pickle


"""
NQClient

Implements asyncio client

args:
    config: NQConfig object

"""
class NQClient(object):

    def __init__(self, config):
        self.config = config

    """
    Async event loop
    """
    async def main(self, data):
        factory = lambda: NQClientProto(data, future)
        loop = asyncio.get_running_loop()

        while True:
            # skipped once to get an initial set of data to initialize the client
            # with by sending an 'init' query
            query = data.get('query')
            if not len(query) or query[0] != 'init':
                data["query"] = input(f'{data.get("prompt")}').split(' ')

            data = pickle.dumps(data)
            future = loop.create_future()

            # wait for protocol to couple with transport
            trans, proto = await loop.create_connection(factory,
                    self.config.get('client_address'),
                    self.config.get('client_port'))

            # wait for data
            await future

            data = pickle.loads(future.result())

            result = data.get('result')
            if result.get('quit'):
                break
            elif result.get('init'):
                print('client initialized')
            else:
                # show data received
                print(result)

        print('goodbye.')

    """
    Start responding to messages
    """
    def start(self):
        asyncio.run(self.main({'query': ['init'], 'result': {}}))


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
        transport.write(self.data)

    """
    Callback triggered when a connection is lost
    """
    def connection_lost(self, exc):
        self.transport.close()

