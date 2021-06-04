import json
import requests

from urllib.parse import urljoin, urlencode

from .exceptions import BinanceException
from .util import timestamp, logger


class BinanceRequest(object):
    def __init__(self, nonce=0, auth=None, headers={}, params=None):
        self.nonce = nonce
        self.auth = auth
        self.headers = headers
        self.params = params

    def getEndpoint(self):
        return urljoin(self.auth.getApiBaseUrl(), self.getPath())

    def getHeaders(self):
        return self.prepareHeaders(self.headers)

    def getMethod(self):
        pass

    def getNonce(self):
        return self.nonce

    def getParams(self):
        self.validateParams(self.params)
        return self.prepareParams(self.params)

    def getPath(self):
        return '/'

    def prepareHeaders(self, headers):
        return headers

    def prepareParams(self, params):
        return params

    def validateParams(self, params):
        pass

    def doRequest(self, endpoint, method, headers=None, params=None):
        pass

    def execute(self):
        try:
            response = self.doRequest(self.getEndpoint(), self.getMethod(),
                    headers=self.getHeaders(),
                    params=self.getParams())

            if response.status_code != 200:
                raise BinanceException(response)

            self.logResponse(self.getNonce(), response)

            return self.handleResponse(response)
        except Exception as e:
            logger.exception(e)

    def handleResponse(self, response):
        return response.json()

    def logRequest(self, nonce, endpoint, headers, params):
        logger.debug(f'{nonce}: <PING> [{self.getMethod()} {endpoint}] headers: {json.dumps(headers)}, params:{json.dumps(params)}')

    def logResponse(self, nonce, response):
        data = response.json()
        logger.debug(f'{nonce}: <PONG> [{response.status_code}] {json.dumps(data)}')


class BinanceGetRequest(BinanceRequest):
    def getMethod(self):
        return 'GET'

    def doRequest(self, endpoint, method, headers=None, params=None):
        self.logRequest(self.getNonce(), endpoint, headers, params)
        return requests.get(endpoint, headers=headers, params=params)


class BinancePostRequest(BinanceRequest):
    def getMethod(self):
        return 'POST'

    def doRequest(self, endpoint, method, headers=None, params=None):
        self.logRequest(self.getNonce(), endpoint, headers, params)
        return requests.post(endpoint, headers=headers, params=params)

    def prepareHeaders(self, headers):
        headers['X-MBX-APIKEY'] = self.auth.getApiKey()
        return headers

    def prepareParams(self, params):
        params['timestamp'] = timestamp()
        params['signature'] = self.auth.signParams(params)
        return params
