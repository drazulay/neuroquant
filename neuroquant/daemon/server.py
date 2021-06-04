import asyncio

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

    def data_received(self, data):
        try:
            msg = data.decode()
            print(f'[{self.client_host}:{self.client_port}] "{msg}"')

            # todo: some intelligent command processing
            # todo: minimize attack surface
            if msg == 'q' or msg == 'quit':
                self.transport.close()
                print(f'[{self.client_host}:{self.client_port}] disconnected')
            else:
                # dispatch message somewhere
                # then send back the results
                result = self.dispatcher.parse(msg)
                self.transport.write(result)
        except Exception as e:
            self.transport.write(e)
            self.transport.close()

if __name__ == '__main__':
    server = NQServer()
    server.start()

