# NeuroQuant

!! WIP !!

A highly neurotic crypto trading bot

Will do stuff on binance so I don't have to

<img src="https://i.ytimg.com/vi/Hcb0Uvid4k0/maxresdefault.jpg"></img>

## Client-Server example

Client:
```
drazulay@dmbp Developer/drazulay/nq (git)-[master] % python neuroquant.py
client initialized
(nq)> help
{'commands': ['info', 'iddqd', 'idkfa', 'init', 'help', 'quit', 'back'], 'sections': ['nq', 'ml', 'binance']}
(nq)> idkfa name=daniel
{'result': 'daniel now has all keys and full ammo!'}
```

Server:
```
drazulay@dmbp Developer/drazulay/nq (git)-[master] % python neuroquant.py --daemon                                                    :(
[127.0.0.1:61646] connected
[127.0.0.1:61646] processing query: init
[127.0.0.1:61646] disconnected
[127.0.0.1:61647] connected
[127.0.0.1:61647] processing query: help
[127.0.0.1:61647] disconnected
[127.0.0.1:61648] connected
[127.0.0.1:61648] processing query: idkfa name=daniel
{'description': 'Keys, full ammo', 'class': 'NQCommandEaster', 'method': 'idkfa', 'args': [], 'kwargs': {'name': '!str'}}
() {'name': 'daniel'}
[127.0.0.1:61648] disconnected
```

## TODO (non-exhaustive)

In general:

- make utils a toplevel module and use the logger everywhere instead of print()
- ip restriction for server
- finish binance api
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
- encrypt communication
- sign messages w. hmac
- compression
- identify as user or as bot, each gets different sets of commands

/cli/command_tree.py:
- ur dangerops (eval used to instantiate command classes from config, sanitize or find another way)
