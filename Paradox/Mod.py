import re


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

        try:
            mod['name'] = re.search('^name[ \t]*=[ \t]*"(.*)"', data, re.MULTILINE).group(1)
            mod['version'] = re.search('^supported_version[ \t]*=[ \t]*"(.*)"', data, re.MULTILINE).group(1)
        except AttributeError as e:
            raise ValueError("Could not find plugin name", data) from e

        return mod
