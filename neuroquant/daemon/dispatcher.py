"""
NQDispatcher

Implements command dispatcher

args:
    command_tree: NQCommandTree instance

"""
class NQDispatcher(object):

    def __init__(self, command_tree):
        self.command_tree = command_tree

    def get_initial_data(self):
        self.command_tree.load()
        section = self.command_tree.get_section()

        return {"commands": self.command_tree.get_commands(),
                "depth": 0,
                "query": [],
                "result": {"init": True},
                "prompt": self.get_prompt(section),
                "section": section}

    def dispatch(self, data):
        section = data.get('section')
        depth = self.command_tree.get_depth(section)
        commands = self.command_tree.get_commands(depth)
        
        # TODO: query parser
        query = data.get('query')
        self.query = query
        self.current_depth = query.get('depth')
        
        # no need to process this data, just make sure a key 'quit' exists
        # in the result so the client knows we understood
        if query[0] == 'quit':
            data['result'] = {"quit": True}
            return data

        if query[0] == 'init':
            return self.get_initial_data()

        # .. do stuf here
        # .. call some code
        # .. determine what the user can do next
        # .. implement commands in a tree structure


        return {"commands": self.get_commands(),
                "depth": self.get_depth(),
                "query": self.get_query(),
                "result": self.get_result(),
                "prompt": self.get_prompt(),
                "section": self.get_section()}

    def validate_query(selfi, query):
        if not len(query):
            raise ValueError(f'zero length query')
        if query[0] not in self.get_commands():
            raise ValueError(f'query {query[0]} not valid for section {self.get_section()}')


    def get_commands(self):
        return self.default_cmds

    def get_depth(self):
        return self.current_depth

    def get_query(self):
        return self.query

    def get_result(self):
        #return self.query_result
        return {"data":f"did some {query[0]}ing over at the ole' dispatcher"}

    def get_prompt(self, section):
        return f'({section})> '

    def get_section(self):
        return self.current_section
