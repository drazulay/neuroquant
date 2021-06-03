import hashlib
import hmac
import json
from urllib.parse import urlencode


class BinanceAuth(object):
    def __init__(self, authfile):
        with open(authfile, 'r') as fp:
            auth = json.load(fp)
            fp.close()
        self.auth = auth

    def getApiKey(self):
        return self.auth.get('api_key')

    def getApiSecret(self):
        return self.auth.get('api_secret')

    def getApiBaseUrl(self):
        return self.auth.get('api_base_url')

    def signParams(self, params):
        return hmac.new(self.getApiSecret().encode('utf-8'),
                urlencode(params).encode('utf-8'),
                hashlib.sha256).hexdigest()
