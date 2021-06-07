import json


"""
NQConfig

Reads and writes json configuration
"""
class NQConfig(dict):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename

        with open(filename, 'r') as fp:
            self.update(json.load(fp))
            fp.close()

    def write(self, key, value):
        client = self.get("client")
        if client is None:
            client = {}

        client["key"] = value
        self["client"] = client

        with open(self.filename, 'w+') as fp:
            config = json.dumps(self, sort_keys=True, indent=4)
            fp.write(config)
            fp.close()

        print("Configuration updated")

