import pickle
import base64
import time
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


"""
NQCryptoClient

This class represents a client that wishes to engage in encrypted communication
with a server.
"""
class NQCryptoClient(object):
    def __init__(self):
        self._privkey = self._create_privkey()
        self._pubkey = self._privkey.public_key()

        self._cipher = None
        self._assoc_pubkey = None

    def _randomsleep(self):
        time.sleep(1.0 / sum(list(os.urandom(32))))

    def _unserialize_pubkey(self, pubkey):
        return serialization.load_der_public_key(pubkey)

    def _create_privkey(self):
        self._randomsleep()
        return X25519PrivateKey.generate()

    def _create_cipher(self,
            salt,
            length=32,
            algorithm=hashes.SHA256(),
            info=None):

        self._randomsleep()
        return Fernet(base64.urlsafe_b64encode(HKDF(
            algorithm=algorithm,
            length=length,
            salt=salt,
            info=info).derive(
                self._privkey.exchange(
                    self._unserialize_pubkey(self._assoc_pubkey)))))           

    """
    Associate a server using its public key

    args:
        - pubkey: the server's serialized public key
        - salt:   a bytestring, preferably os.urandom(16), sent by the client
                  initiating communication, to be used as salt for the cipher. 
    """
    def associate(self, pubkey, salt):
        self._assoc_pubkey = pubkey
        self._cipher = self._create_cipher(salt)

        return self.get_public_key()

    """
    Encrypt a message
    """
    def encrypt(self, message):
        return self._cipher.encrypt(pickle.dumps(message))

    """
    Decrypt a message
    """
    def decrypt(self, message):
        return pickle.loads(self._cipher.decrypt(message))

    def get_public_key(self, serialized=True):
        if serialized:
            return self._pubkey.public_bytes(
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                    encoding=serialization.Encoding.DER)

        return self._pubkey


"""
NQCryptoServer

This class acts as a server that can associate multiple peers by their public
keys, using unique keypairs for the key exchanges with each of them.
"""
class NQCryptoServer(NQCryptoClient):
    def __init__(self, *args, **kwargs):
        self._clients = {}

        super().__init__(*args, **kwargs)

    def _get_client(self, client_pubkey):
        peer = self._clients.get(client_pubkey)
        if peer is not None:
            return peer

        raise Exception(f'Client not associated: {client_pubkey})')


    """
    Associate a client using its public key

    args:
        - pubkey: the client's serialized public key
        - salt:   a bytestring, preferably os.urandom(16), sent by the client
                  initiating communication, to be used as salt for the cipher. 

    returns:
        - server_pubkey: the public key that the client should use for
                         associating with the server so the correct shared
                         cipher is generated.
    """
    def associate(self, pubkey, salt):
        print(f'Associating client: {pubkey}')
        client = NQCryptoClient()
        server_pubkey = client.associate(pubkey, salt)
        self._clients[pubkey] = client

        return server_pubkey

    """
    Encrypt a message

    args:
        - message: the message to be encrypted
        - pubkey: the client's serialized public key
    """
    def encrypt(self, message, pubkey):
        return self._get_client(pubkey).encrypt(message)

    """
    Decrypt a message
        - message: the message to be decrypted
        - pubkey: the client's serialized public key
    """
    def decrypt(self, message, pubkey):
        return self._get_client(pubkey).decrypt(message)

if __name__ == '__main__':
    server = NQCryptoServer()

    # Associate client A
    clientA = NQCryptoClient()
    salt = os.urandom(16)
    clientA_pubkey = clientA.get_public_key()
    server_pubkey = server.associate(clientA_pubkey, salt)
    clientA.associate(server_pubkey, salt)

    enc = server.encrypt('message from server to A', pubkey=clientA_pubkey)
    print(clientA.decrypt(enc))
    enc = clientA.encrypt('message from A to server')
    print(server.decrypt(enc, pubkey=clientA_pubkey))

    # Associate client B
    clientB = NQCryptoClient()
    salt = os.urandom(16)
    clientB_pubkey = clientB.get_public_key()
    server_pubkey = server.associate(clientB_pubkey, salt)
    clientB.associate(server_pubkey, salt)

    enc = server.encrypt('message from server to B', pubkey=clientB_pubkey)
    print(clientB.decrypt(enc))
    enc = clientB.encrypt('message from B to server')
    print(server.decrypt(enc, pubkey=clientB_pubkey))

