import asyncio

class NQClient(asyncio.Protocol):
    def __init__(self, message, future):
        self.message = message
        self.future = future

    def connection_made(self, transport):
        transport.write(self.message.encode())

    def data_received(self, data):
        self.future.set_result(f'{data.decode()}')

    def connection_lost(self, exc):
        self.future.set_result("%quit")


async def main():
    protocol_factory = lambda: NQClient(data, future)

    loop = asyncio.get_running_loop()

    while True:
        data = input('> ')
        future = loop.create_future()
        
        # wait for protocol to couple with transport
        # todo: get host/port from json file
        transport, protocol = await loop.create_connection(protocol_factory,
                '127.0.0.1', 8181)

        # wait for data
        await future

        data = future.result()
        if data == '%quit':
            break

        # show data received
        print(data)

    print('Quitting..')

asyncio.run(main())
