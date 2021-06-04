import asyncio
import pickle

from dispatcher import NQDispatcher

"""
NQServer

Implements asyncio server

args:
    config: NQConfig object

"""
class NQServer(object):
    def __init__(self, config):
        self.config = config

    async def main(self):
        loop = asyncio.get_running_loop()
        factory = lambda: NQServerProto(NQDispatcher())
        server = await loop.create_server(factory,
                self.config.get('server_address'),
                self.config.get('server_port'))

        async with server:
            await server.serve_forever()

    def start(self):
        asyncio.run(self.main())

"""
NQServerProto

Implements asyncio server protocol handler

args:
    dispatcher: NQDispatcher instance

"""
class NQServerProto(asyncio.Protocol):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.client_host = None
        self.client_port = None

        super().__init__()

    """
    Callback triggered data is received
    """
    def data_received(self, data):
        data = pickle.dumps(self.dispatcher.dispatch(pickle.loads(data)))
        
        # send data to client
        self.transport.write(data)

    """
    Callback triggered when a connection is established
    """
    def connection_made(self, transport):
        self.transport = transport
        host, port = transport.get_extra_info('peername')
        self.client_host = host
        self.client_port = port
        print(f'[{self.client_host}:{self.client_port}] connected')

    """
    Callback triggered when a connection is lost
    """
    def connection_lost(self, exc):
        if isinstance(exc, Exception):
            print(f'[{self.client_host}:{self.client_port}] exception: {exc}')
        print(f'[{self.client_host}:{self.client_port}] disconnected')

        self.transport.close()


if __name__ == '__main__':
    server = NQServer()
    server.start()

