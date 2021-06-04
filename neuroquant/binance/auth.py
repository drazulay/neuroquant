import hashlib
import hmac
import json

from urllib.parse import urlencode

from ..config import NQConfig


class BinanceAuth(NQConfig):
    def getApiKey(self):
        return self.get('api_key')

    def getApiSecret(self):
        return self.get('api_secret')

    def getApiBaseUrl(self):
        return self.get('api_base_url')

    def signParams(self, params):
        return hmac.new(self.getApiSecret().encode('utf-8'),
                urlencode(params).encode('utf-8'),
                hashlib.sha256).hexdigest()
