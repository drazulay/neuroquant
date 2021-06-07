import asyncio
import pickle
import traceback

from .dispatcher import NQDispatcher
from ..cli import NQCommandTree
from ..crypto import NQCryptoServer

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
        print(f'Starting server..')
        loop = asyncio.get_running_loop()

        command_tree = NQCommandTree(self.config)
        command_tree.load()
        
        crypto = NQCryptoServer(self.config)
        factory = lambda: NQServerProto(NQDispatcher(command_tree), crypto)

        host = self.config.get('host_address')
        port = self.config.get('host_port')
        server = await loop.create_server(factory, host, port)

        async with server:
            print(f'Listening for connections on {host}:{port}')
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
    def __init__(self, dispatcher, crypto):
        self.dispatcher = dispatcher
        self.client_host = None
        self.client_port = None
        self.crypto = crypto

        super().__init__()

    """
    Callback triggered when data is received
    """
    def data_received(self, data):
        data = pickle.loads(data)

        # todo: how do we agree on salt without sending it over the wire?
        #       this undoubtedly makes the encryption easier to break..
        #       maybe we should use a kdf that uses a nonce instead?
        #       hmm, google thinks unencrypted salts are no problemo..
        #       bigger cryptobrain needed
        if type(data) is dict and data.get('handshake'):
            #print('----handshake---')
            pk = self.crypto.associate(
                    data.get('pubkey'),
                    data.get('salt'))
        else:
            pk = data.get('pubkey')
            message = data.get('message')
            if type(message) is bytes:
                message = self.crypto.decrypt(message, pk)

            query = message.get('query')

            if query == 'save_client_keys':
                message["result"] = {"save_client_keys": True}
            else:
                try:
                    print(f'[{self.client_host}:{self.client_port}] processing query: {query}')

                    message = self.dispatcher.dispatch(message)
                except Exception as e:
                    errors = [e]
                    message['errors'] = errors
                    traceback.print_exc()

            data['message'] = self.crypto.encrypt(message, pk)

        data['pubkey'] = pk
        data['stop'] = False # not used atm

        self.transport.write(pickle.dumps(data))
        self.transport.close()


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

