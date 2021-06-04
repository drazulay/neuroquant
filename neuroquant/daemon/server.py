import asyncio
import pickle

from dispatcher import NQDispatcher

class NQServer(object):
    async def main(self):
        loop = asyncio.get_running_loop()

        protocol_factory = lambda: NQServerProto(NQDispatcher())
        server = await loop.create_server(protocol_factory, '127.0.0.1', 8181)

        async with server:
            await server.serve_forever()

    def start(self):
        asyncio.run(self.main())

class NQServerProto(asyncio.Protocol):
    def __init__(self, dispatcher, *args, **kwargs):
        self.dispatcher = dispatcher
        self.client_host = None
        self.client_port = None

        super().__init__(*args, **kwargs)

    def connection_made(self, transport):
        self.transport = transport
        host, port = transport.get_extra_info('peername')
        self.client_host = host
        self.client_port = port
        print(f'[{self.client_host}:{self.client_port}] connected')

    def connection_lost(self, exc):
        print(f'[{self.client_host}:{self.client_port}] disconnected')

    # todo:
    # send structured data to client based on query:
    # {
    #   "commands": [...],      -> list of available commands based on section
    #   "depth": 1,             -> depth in section tree
    #   "query": ["help"],      -> last entered query
    #   "result": {...},        -> result of last entered query
    #   "prompt": "(algo)> ",   -> prompt to show user
    #   "section": "algo",      -> currently active section
    # } 
    # .. and send it back
    # 
    def data_received(self, data):
        data = pickle.loads(data)
        query = data.get('query')

        # user should be able to quit at any time
        if query[0] == 'quit':
            self.transport.close()
        else:
            # parse the data and get modified parts back
            depth, section, res, cmds = self.dispatcher.dispatch(data)
            
            # Set prompt based on active section
            prompt = f'({section})> '
            
            # build new data and pickle it
            data = pickle.dumps({"commands": cmds,
                    "depth": depth,
                    "query": ["none"],
                    "result": res,
                    "prompt": prompt,
                    "section": section})

            # send data to client
            self.transport.write(data)

if __name__ == '__main__':
    server = NQServer()
    server.start()

