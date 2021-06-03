from auth import BinanceAuth
from api import BinanceAPI
from util import logger

if __name__ == '__main__':
    logger.info('Creating API instance..')
    auth = BinanceAuth(authfile='auth.json')
    api = BinanceAPI(auth=auth)

    # Test Order
    params = {
            'symbol': 'ETHUSDT',
            'side': 'SELL',
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': 0.1,
            'price': 2826.24,
            'recvWindow': 5000
            }

    api.postTestOrder(params)
