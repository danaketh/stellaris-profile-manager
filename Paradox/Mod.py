from pyparsing import *


class Mod:
    """
    Parser for mod files
    """

    def __init__(self, file_path):
        """
        Init
        :param file_path: 
        """
        f = open(file_path, mode='r')
        self.data = f.read()
        f.close()

    def get_info(self):
        return self.parse(self.data)

    @staticmethod
    def parse(data):
        """
        Parse the file
        :param data: 
        :return: 
        """
        mod = {}

        lbrack = Literal("{").suppress()
        rbrack = Literal("}").suppress()
        equals = Literal("=").suppress()

        nonequals = "".join([c for c in printables if c != "="]) + " \t"

        keydef = ~lbrack + Word(nonequals) + equals + restOfLine
        arraydef = ~lbrack + Word(nonequals) + equals + lbrack + restOfLine + rbrack

        conf = Dict(
            ZeroOrMore(
                Group(keydef),
                Group(arraydef)
            )
        )

        tokens = conf.parseString(data)
        for t in tokens.asList():
            val = t[1]
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]

            mod[t[0]] = val

        return mod
