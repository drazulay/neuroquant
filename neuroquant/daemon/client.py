import asyncio
import pickle

class NQClient(asyncio.Protocol):
    def __init__(self, message, future):
        self.message = message
        self.future = future

    def connection_made(self, transport):
        self.transport = transport
        transport.write(self.message)

    def data_received(self, data):
        self.future.set_result(data)

    def connection_lost(self, exc):
        print('disconnected')
        self.future.set_result(pickle.dumps({"result": {"quit": True}}))
        self.transport.close()

async def main():
    # receive structured data from server:
    # {
    #   "commands": {...},      -> list of available commands based on section
    #   "depth": 1,             -> depth in section tree
    #   "query": ["help"],      -> last entered query
    #   "result": {...},        -> result of last entered query
    #   "prompt": "(algo)> ",   -> prompt to show user
    #   "section": "algo",      -> currently active section
    # } 
    #

    factory = lambda: NQClient(data, future)
    loop = asyncio.get_running_loop()

    query = ['init']
    data = {'query': query, 'result': {}}

    while True:
        # skipped once to get an initial set of data to initialize the client
        # with by sending an 'init' query
        query = data.get('query')
        if not len(query) or query[0] != 'init':
            data["query"] = input(f'{data.get("prompt")}').split(' ')

        data = pickle.dumps(data)
        future = loop.create_future()
        
        # wait for protocol to couple with transport
        # todo: get host/port from json file
        trans, proto = await loop.create_connection(factory, '127.0.0.1', 8181)

        # wait for data
        await future

        data = pickle.loads(future.result())

        result = data.get('result')
        if result.get('quit') != None:
            break
        elif result.get('init') != None:
            print('Client initialized')
        else:
            # show data received
            print(result)

    print('Quitting..')

asyncio.run(main())
