import argparse

from neuroquant import NQServer, NQClient, NQConfig

class NeuroQuant(object):
    def __init__(self, config_filename):
        self.config_filename = config_filename

    def get_server(self):
        return NQServer(NQConfig(self.config_filename))

    def get_client(self):
        return NQClient(NQConfig(self.config_filename))


parser = argparse.ArgumentParser(prog='neuroquant')
parser.add_argument('-c', '--config', default="etc/config.json")
parser.add_argument('--daemon', action='store_true')

args = parser.parse_args()

nq = NeuroQuant(args.config)
if args.daemon:
    nq.get_server().start()
else:
    nq.get_client().start()
