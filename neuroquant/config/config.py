import json


"""
NQConfig

Loads configuration from json
"""
class NQConfig(dict):
    def __init__(self, filename, *args, **kwargs):
        with open(filename, 'r') as fp:
            self.update(json.load(fp))
            fp.close()
