# NeuroQuant

!! WIP !!

A highly neurotic crypto trading bot

Will do stuff on binance so I don't have to

<img src="https://i.ytimg.com/vi/Hcb0Uvid4k0/maxresdefault.jpg"></img>

## Client-Server example

Client:
```
drazulay@dmbp Developer/drazulay/nq (git)-[master] % python neuroquant.py
Secure channel established
(nq)> help
{'commands': ['info', 'iddqd', 'idkfa', 'init', 'help', 'quit', 'back'], 'sections': ['nq', 'ml', 'binance']}
(nq)> iddqd name=Daniel
{'result': 'Daniel now has God Mode!'}
(nq)>
```

Server:
```
drazulay@dmbp Developer/drazulay/nq (git)-[master] % python neuroquant.py --daemon
Starting server..
Listening for connections on 127.0.0.1:8181
[127.0.0.1:53735] connected
Associating client: b'0*0\x05\x06\x03+en\x03!\x00f\xf7+\xe4\x01\xd2\xfe\xef\x07\xfd\xa4\xfb\xc0-vcud\x1fk\xeb\x87A\x92\xfd\xd2d"\x0b\xe1\x82b'
[127.0.0.1:53735] disconnected
[127.0.0.1:53736] connected
[127.0.0.1:53736] processing query: help
[127.0.0.1:53736] disconnected
[127.0.0.1:53737] connected
[127.0.0.1:53737] processing query: iddqd name=Daniel
{'description': 'God mode', 'class': 'NQCommandEaster', 'method': 'iddqd', 'args': [], 'kwargs': {'name': '!str'}}
() {'name': 'Daniel'}
[127.0.0.1:53737] disconnected
```

## TODO (non-exhaustive)

In general:

- make utils a toplevel module and use the logger everywhere instead of print()
- ip restriction for server
- finish binance api
- pluggable exchange api's?
- 'test mode' where binance calls are not actually made
- collect statistics on trades/funds and provide some analytics commands
- implement bot as a client and give it its own set of commands for using the binance api
- a working (sklearn/pytorch?) model for time series prediction
- backtesting for models
- echo state network for time series prediction (just cause)

Found in source:

/daemon/dispatcher.py:
- pretty output with full help
- help on keyword

/daemon/client.py:
- get 'renderer' to use from received data and use that to render the result in the way the server intends
- compression
- identify as user or as bot, each gets different sets of commands

/cli/command_tree.py:
- ur dangerops (eval used to instantiate command classes from config, use getattr or importlib)
