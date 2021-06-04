from command import NQCommand

"""
NQSectionNode

Holds data for a single section
Instantiates NQCommand instances for each command in the section
"""
class NQSectionNode(object):
    def __init__(self, section, commands, parent=None):
        for k, definition in commands.items():
            commands[k] = NQCommand(definition)

        self.commands = commands
        self.parent = parent
        self.section = section


"""
NQCommandTree

Holds a tree of all commands defined in config
"""
class NQCommandTree(object):
    def __init__(self, config):
        self.config = config
        self.root = None

    """
    Recursively create NQSectionNode instances from command sections in config
    """
    def load(self, section=None):
        if section is None:
            section = self.config.get('cli.commands')

        root = NQSectionNode(section.get('section'),
                section.get('commands'), self.root)

        for subsection in section.get('subsections'):
            self.load(subsection)

        self.root = root

