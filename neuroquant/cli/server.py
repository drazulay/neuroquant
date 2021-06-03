import asyncio


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print(f'<< dispatching "{message}"')

        if message == 'quit':
            self.transport.write(data)
            self.transport.close()
        else:
            # do something with message
            # then send back the results
            result = b'some cool results'
            print(f'>> {result}')
            self.transport.write(result)


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 8181)

    async with server:
        await server.serve_forever()

asyncio.run(main())

