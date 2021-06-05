from .commands import *

"""
NQSectionNode

Holds data for a single section
Instantiates NQCommand instances for each command in the section
"""
class NQSectionNode(object):
    def __init__(self, section, commands, parent=None):
        for k, definition in commands.items():
            # todo: ur dangerops
            commands[k] = eval(f'{definition.get("class")}(definition)')

        self.commands = commands
        self.parent = parent
        self.section = section

    def get_section(self):
        return self.section

    def get_commands(self):
        return self.commands

    def get_parent(self):
        if self.parent is None:
            return self
        return self.parent


"""
NQCommandTree

Holds a tree of all commands defined in config
"""
class NQCommandTree(object):
    def __init__(self, config):
        self.config = config
        self.root = None
        self.nodes = []
        self.sections = []

    """
    Recursively create NQSectionNode instances from command sections in config
    """
    def load(self, section=None, parent=None):
        if parent is None:
            section = self.config.get('cli').get('commands')
            self.root = NQSectionNode(section.get('section'),
                    section.get('commands'))
            current = self.root
        else:
            current = NQSectionNode(section.get('section'),
                    section.get('commands'), parent)

        self.sections.append(current.get_section())
        self.nodes.append(current)

        for subsection in section.get('subsections'):
            self.load(subsection, current)

    def get_node(self, section):
        for node in self.nodes:
            if node.get_section() == section:
                return node

    def get_root(self):
        return self.root

    def get_sections(self):
        return self.sections

    def get_commands(self, section):
        if self.root.get_section() == section:
            return self.root.get_commands()
        
        for node in self.nodes:
            if node.get_section() == section:
                return node.get_commands()

        return {}

