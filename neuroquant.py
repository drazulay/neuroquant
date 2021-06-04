import argparse

from neuroquant import NQServer, NQClient, NQConfig

class NeuroQuant(object):
    def __init__(self, config_filename):
        self.config_filename = config_filename

    def get_config(self):
        return NQConfig(self.config_filename)

    def start_server(self):
        return lambda: NQServer(self.get_config())

    def start_client(self):
        return NQClient(self.get_config())


parser = argparse.ArgumentParser(prog='neuroquant')
parser.add_argument('-c', '--config')
parser.add_argument('--daemon', action='store_true')

args = parser.parse_args()
print(args)







