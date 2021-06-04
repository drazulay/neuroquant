"""
NQDispatcher

Implements command dispatcher

args:
    command_tree: NQCommandTree instance

"""
class NQDispatcher(object):

    def __init__(self, command_tree):
        self.command_tree = command_tree
        self.global_commands = ["help", "quit", "back"]

    def get_initial_data(self):
        section = self.command_tree.get_root().get_section()

        return {"commands": self.command_tree.get_commands(section),
                "query": [],
                "result": {"init": True},
                "prompt": self.get_prompt(section),
                "section": section}

    def dispatch(self, data):
        query = data.get('query')
        if not len(query):
            raise ValueError(f'zero length query')

        command = query[0]

        if command == 'init':
            return self.get_initial_data()

        if command == 'quit':
            data['result'] = {"quit": True}
            return data

        section = data.get('section')
        commands = self.command_tree.get_commands(section)
        command_keys = list(commands.keys())

        if command == 'back':
            node = self.command_tree.get_node(section).get_parent()
            section = node.get_section()
            commands = node.get_commands()

        sections = self.command_tree.get_sections()
        if command in sections:
            section = command
            commands = self.command_tree.get_commands(section)

        # todo: pretty output with full help
        if command == 'help':
            command_keys.extend(self.global_commands)
            data['result'] = {"commands": command_keys, "sections": sections}
            return data
        
        if command not in command_keys:
            raise ValueError(f'query {command} not valid for section {self.get_section()}')

        command_instance = commands[command]
        args, kwargs = self.parse_query(query[1:])
        result = command_instance.execute(*args, **kwargs)

        return {"commands": self.command_tree.get_commands(section),
                "query": query,
                "result": result,
                "prompt": self.get_prompt(section),
                "section": section}

    def parse_query(self, query):
        args = []
        kwargs = {}

        for part in query:
            if part.find('=') >= 0:
                k, v = part.split('=')
                kwargs[k] = v
            else:
                args.append(part)

        return (args, kwargs)

    def execute_command(self, command, *args):
        return 

    def get_prompt(self, section):
        return f'({section})> '
