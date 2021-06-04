import json

from .util import logger
from .req import BinanceGetRequest, BinancePostRequest


class GetServerTime(BinanceGetRequest):
    def getPath(self):
        return '/api/v1/time'

    def handleResponse(self, response):
        data = response.json()
        return data['serverTime']


class GetResponseTime(GetServerTime):
    def handleResponse(self, response):
        server_time = super().handleResponse(response)
        return self.getTimestamp() - server_time


class PostOrder(BinancePostRequest):
    def getPath(self):
        return '/api/v3/order'

    def validateParams(self, params):
        pass

    def handleResponse(self, response):
        return response


class PostTestOrder(BinancePostRequest):
    def getPath(self):
        return '/api/v3/order/test'

    def validateParams(self, params):
        pass

    def handleResponse(self, response):
        return response


class BinanceAPI(object):
    def __init__(self, auth=None):
        self._auth = auth
        self._nonce = 0

        super().__init__()

    def nonce(self):
        self._nonce += 1
        return self._nonce

    def getServerTime(self):
        request = GetServerTime(self.nonce(), auth=self._auth)
        return request.execute()

    def postOrder(self, params):
        request = PostOrderRequest(self.nonce(), auth=self._auth, params=params)
        return request.execute()

    def postTestOrder(self, params):
        request = PostTestOrder(self.nonce(), auth=self._auth,
                params=params)
        return request.execute()
