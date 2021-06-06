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
NQCryptoPeer

This class represents a peer that wishes to engage in encrypted communication
with other peers.

Explanation:
    I hope... this implements an elleptic curve diffie-hellman ephemeral type
    key exchange (ECDHE).

    see: https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman

    Two peers, Peer A and Peer B, both instantiate an NQCryptoPeer object.

    Peer A calls NQCryptoPeer.get_public_key() to get its public key and then
    sends this public key to Peer B.

    Peer B then calls NQCrypto.exchange() with the public key received from
    Peer A. This method will store Peer B's shared secret locally and then
    return another public key, which Peer B will send back to Peer A.

    Peer A will now also call NQCrypto.exchange() but with Peer B's public key,
    to store Peer A's version of the shared secret locally.

    At this point both peers should have the same shared secret stored locally.
    This shared secret has been turned into identical fernet keys that both
    peers can use to encrypt and decrypt messages from each other.
"""
class NQCryptoPeer(object):
    def __init__(self, peers={}, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._peers = peers
        self._shared_key = None

        self._generate_keypair()


    def _get_peer(self, peer_pubkey):
        peer = self._peers.get(peer_pubkey)
        if peer is None:
            raise Exception(f'Handshake not performed for key: {peer_pubkey}')
        return peer

    def _load_peer_pubkey(self, peer_pubkey):
        return serialization.load_der_public_key(peer_pubkey)

    def _generate_keypair(self, salt=b'nq'):
        print('Generating keypair..')
        self._privkey = X25519PrivateKey.generate()
        time.sleep(1.0 / sum(list(os.urandom(32))))
        self._pubkey = self._privkey.public_key()
        time.sleep(1.0 / sum(list(os.urandom(32))))
        print(f'Public key: {self.get_public_key()}')

    def create_cipher(self, salt):
            print('Creating shared cipher..')
            # derive key
            kdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                info=None,
            )
            derived_key = kdf.derive(self._shared_key)
            cipher = Fernet(base64.urlsafe_b64encode(derived_key))           
            time.sleep(1.0 / sum(list(os.urandom(32))))
            return cipher

    def get_public_key(self, serialized=True):
        if serialized:
            return self._pubkey.public_bytes(
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                    encoding=serialization.Encoding.DER)

        return self._pubkey

    """
    Exchange public keys for diffie-helmann exchange

    TODO: Use a different keypair with each peer to prevent patterns in the
          encrypted data. Is this still a thing with Fernet (uses HMAC)?

    The salt should be sent by the peer initiating communication, preferably by
    using os.urandom(16). It must be used by both peers to create the fernet
    key.
    """
    def exchange(self, pubkey, salt=b'nq'):
        peer_pubkey = self._load_peer_pubkey(pubkey)
        print('Performing Diffie-Hellman exchange..')
        # diffie-hellman key exchange
        self._shared_key = self._privkey.exchange(peer_pubkey)
        time.sleep(1.0 / sum(list(os.urandom(32))))
        self._peers[pubkey] = self.create_cipher(salt)
        time.sleep(1.0 / sum(list(os.urandom(32))))

        return self.get_public_key()

    """
    Encrypt a message for peer to which peer_pubkey belongs
    """
    def encrypt(self, data, peer_pubkey=None):
        cipher = self._get_peer(peer_pubkey)
        return f.encrypt(pickle.dumps(data))

    """
    Decrypt a message from peer to which peer_pubkey belongs
    """
    def decrypt(self, data, peer_pubkey=None):
        cipher = self._get_peer(peer_pubkey)
        return pickle.loads(f.decrypt(data))

if __name__ == '__main__':
    peerA = NQCryptoPeer()
    peerB = NQCryptoPeer()

    pubB = peerB.exchange(peerA.get_public_key())
    pubA = peerA.exchange(peerB.get_public_key())

    enc = peerA.encrypt('hello', peer_pubkey=pubB)
    print(enc)
    dec = peerB.decrypt(enc, peer_pubkey=pubA)
    print(dec)


