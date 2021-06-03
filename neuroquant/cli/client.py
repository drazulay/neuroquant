import asyncio


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, on_receive):
        self.message = message
        self.on_receive = on_receive

    def connection_made(self, transport):
        transport.write(self.message.encode())

    def data_received(self, data):
        self.on_receive.set_result(f'{data.decode()}')


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    while True:
        on_receive = loop.create_future()
        transport, protocol = await loop.create_connection(
                lambda: EchoClientProtocol(input('> '), on_receive), '127.0.0.1', 8181)
        await on_receive
        if on_receive.result() == 'quit':
            break
        print(on_receive.result())

    print('Quitting..')
    transport.close()

asyncio.run(main())
