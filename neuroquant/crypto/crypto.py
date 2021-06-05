import pickle

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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
class NQCryptoPeer(NQCryptoPeer):
    def __init__(self, peers={}, *args, **kwargs):
        self._peers = peers

        self._privkey = ec.generate_private_key(ec.SECP384R1())
        self._pubkey = self.privkey.public_key()
        self._fernet_key = None

        super().__init__(*args, **kwargs)

    def _create_fernet_key(self, peer_pubkey, salt):
        if self._fernet_key = None:
            self._peer_pubkey = peer_pubkey

            # key derivation function
            kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000)
            
            # derived key
            key = kdf.derive(self._privkey.exchange(ec.ECDH(), peer_pubkey))

            self._fernet_key = base64.urlsafe_b64encode(key)

    def _get_fernet_key(self):
        return self._fernet_key

    def _get_peer(self, peer_pubkey):
        peer = self._peers.get(peer_pubkey)
        if peer is None:
            raise Exception('Handshake not performed for key: {peer_pubkey}')

        return peer


    def get_public_key(self):
        return self._pubkey

    """
    Exchange public keys for diffie-helmann exchange

    The salt should be sent by the peer initiating communication, preferably by
    using os.urandom(16). It must be used by both peers to create the fernet
    key.
    """
    def exchange(self, peer_pubkey, salt=b'nq'):
        peer = self._peers.get(peer_pubkey)
        if peer is None:
            peer = NQCryptoPeer()
            peer._create_fernet_key(peer_pubkey, salt)
            self._peers[peer_pubkey] = peer

        return peer.get_public_key()

    """
    Encrypt a message for peer to which peer_pubkey belongs
    """
    def encrypt(self, peer_pubkey, data):
        peer = self._get_peer(peer_pubkey)
        f = Fernet(peer._get_fernet_key())
        return f.encrypt(pickle.dumps(data))

    """
    Decrypt a message from peer to which peer_pubkey belongs
    """
    def encrypt(self, peer_pubkey, token):
        peer = self._get_peer(peer_pubkey)
        f = Fernet(peer._get_fernet_key())
        return pickle.loads(f.decrypt(data))

