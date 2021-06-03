class ValidationException(Exception):
    def __init__(self, params):
        super().__init__(f'Invalid parameter(s): {json.dumps(params)}')

class BinanceException(Exception):
    def __init__(self, response):
        if response.text:
            http_status = response.status_code
            data = response.json()
            super().__init__(f'[HTTP Status {http_status}]: code {data["code"]}: {data["msg"]}')
        else:
            super().__init__(f'[HTTP Status {http_status}]')
