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
        self.global_commands = ["init", "help", "quit", "back"]

    def dispatch(self, data):
        query = data.get('query').split(' ')
        section = data.get('section')

        op = query.pop(0)

        if op in self.global_commands:
            return self.handle_global_command(op, data)

        sections = self.command_tree.get_sections()
        if op in [*sections]:
            return self.create_message(op)

        commands = self.command_tree.get_commands(section)
        if op not in [*commands]:
            raise ValueError(
                    f'query {op} not valid for section {section}')

        command_instance = commands[op]
        args, kwargs = self.parse_query_args(query)

        return self.create_message(data.get('section'),
                result=command_instance.execute(*args, **kwargs))

    def create_message(self, section, result={}):
        return (section,
                self.command_tree.get_commands(section),
                result)

    def handle_global_command(self, cmd, data):
        section = data.get('section')

        if cmd == 'init':
            section = self.command_tree.get_root().get_section()
            return self.create_message(section, result={"init": True})

        if cmd == 'quit':
            return self.create_message(section, result={"quit": True})

        if cmd == 'back':
            node = self.command_tree.get_node(section).get_parent()
            return self.create_message(node.get_section())
                    
        # todo:
        # - pretty output with full help
        # - help on keyword
        if cmd == 'help':
            commands = [*self.command_tree.get_commands(section).keys()]
            commands += self.global_commands
            sections = self.command_tree.get_sections()
            return self.create_message(
                    section,
                    result={"commands": commands, "sections": sections})

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

