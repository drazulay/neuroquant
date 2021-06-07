import re

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

    def dispatch(self, data):
        query = data.get('query').split(' ')
        section = data.get('section')

        op = query.pop(0)

        commands = self.get_commands(section)
        sections = self.command_tree.get_sections()
        if op not in [*commands] and op not in [*sections]:
            raise ValueError(
                    f'query {op} not valid for section {section}')

        if op in self.global_commands:
            return self.handle_global_command(op, data)

        if op in [*sections]:
            return self.create_message(op)

        command_instance = commands[op]
        args, kwargs = self.parse_query_args(query)

        return self.create_message(data.get('section'),
                result=command_instance.execute(*args, **kwargs))

    def get_commands(self, section):
            commands = [*self.command_tree.get_commands(section)]
            commands += self.global_commands
            return commands

    def create_message(self, section, result={}):
        return {"section": section,
                "commands": self.get_commands(section),
                "result": result}

    def handle_global_command(self, cmd, data):
        section = data.get('section')

        if cmd == 'quit':
            return self.create_message(section, result={"quit": True})

        if cmd == 'back':
            node = self.command_tree.get_node(section).get_parent()
            return self.create_message(node.get_section())
                    
        # todo:
        # - pretty output with full help
        # - help on keyword
        if cmd == 'help':
            sections = self.command_tree.get_sections()
            return self.create_message(
                    section,
                    result={"commands": self.get_commands(section),
                        "sections": sections})

    def parse_query_args(self, query):
        args = []
        kwargs = {}

        for part in query:
            if part.find('=') >= 0:
                part = re.sub('[\=]+', '=', part).strip('=')
                k, v = part.split('=')
                kwargs[k] = v
            else:
                args.append(part)

        return (args, kwargs)

