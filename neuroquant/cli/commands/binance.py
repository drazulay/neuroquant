from ..command import NQCommand

class NQCommandBinance(NQCommand):
    def config(self, key, value):
        return f'Binance configuration updated: {key} set to {value}'
