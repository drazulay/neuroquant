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

    args:
        - message: the message to be encrypted
    """
    def encrypt(self, message):
        #print(f'ENCRYPT: {message}')
        if self._cipher is not None:
            return self._cipher.encrypt(pickle.dumps(message))

    """
    Decrypt a message

    args:
        - message: the message to be decrypted
    """
    def decrypt(self, message):
        #print(f'DECRYPT: {message}')
        if self._cipher is not None:
            return pickle.loads(self._cipher.decrypt(message))

    """
    Return the public key that the server can use to associate with the client
    """
    def get_public_key(self):
        return self._pubkey.public_bytes(
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
                encoding=serialization.Encoding.DER)

    """
    Sleep a short random time
    """
    def _randomsleep(self):
        time.sleep(1.0 / sum(list(os.urandom(32))))

    """
    Unserialize a public key

    args:
        - pubkey: a DER-format serialized public key
    """
    def _unserialize_pubkey(self, pubkey):
        return serialization.load_der_public_key(pubkey)

    """
    Create a curve25519 private key for key agreement
    """
    def _create_privkey(self):
        self._randomsleep()
        return X25519PrivateKey.generate()

    """
    Create a Fernet cipher based on the curve25519 Diffie-Hellman shared secret

    args:
        - salt:      a bytestring for the salt
        - length:    the desired key length
        - algorithm: the desired hash algorithm
        - info:      additional information to embed in the cipher
    """
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
NQCryptoServer

This class acts as a server that can associate multiple peers by their public
keys, using unique keypairs for the key exchanges with each of them.
"""
class NQCryptoServer(NQCryptoClient):

    def __init__(self, *args, **kwargs):
        self._clients = {}

        super().__init__(*args, **kwargs)

    """
    Return an associated client by its public key
    
    args:
        - client_pubkey: the client's public key
    """
    def _get_client(self, client_pubkey):
        #print(self._clients)
        peer = self._clients.get(client_pubkey)
        if peer is not None:
            return peer

        raise Exception(f'Client not associated: {client_pubkey})')

    """
    Associate a client using its public key and return the public key that the
    client should use to associate, thereby completing the key exchange.

    args:
        - pubkey: the client's serialized public key
        - salt:   a bytestring, preferably os.urandom(16), sent by the client
                  initiating communication, to be used as salt for the cipher. 
    """
    def associate(self, pubkey, salt):
        print(f'Associating client: {pubkey}')
        client = NQCryptoClient()
        server_pubkey = client.associate(pubkey, salt)
        self._clients[pubkey] = client

        return server_pubkey

    """
    Encrypt a message for a client identified by its public key

    args:
        - message: the message to be encrypted
        - pubkey: the client's serialized public key
    """
    def encrypt(self, message, pubkey):
        return self._get_client(pubkey).encrypt(message)

    """
    Decrypt a message for a client identified by its public key

    args:
        - message: the message to be decrypted
        - pubkey: the client's serialized public key
    """
    def decrypt(self, message, pubkey):
        return self._get_client(pubkey).decrypt(message)

