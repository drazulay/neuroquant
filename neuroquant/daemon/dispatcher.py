class NQDispatcher(object):
    def dispatch(self, data):
        cmds = ["help", "quit"]
        section = "nq"
        query = data.get('query')
        if query[0] == 'quit':
            res = {"quit": True}
        elif query[0] == 'init':
            res = {"init": True}
        elif query[0] not in cmds:
            res = {"error": f'command {query[0]} not valid for section {section}'} 
        else:
            res = {"data":f"did some {query[0]}-ing over at the ole' dispatcher"}
        

        depth = 0
        return (depth, section, res, cmds)
