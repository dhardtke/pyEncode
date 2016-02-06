from configparser import ConfigParser


class Config:
    filename = ""
    config = None

    def __init__(self, filename):
        self.filename = filename
        self.reload()

    def reload(self):
        self.config = ConfigParser()
        self.config.read(self.filename)

    def __setitem__(self, key, value):
        self.config.set(key, value)

    def __getitem__(self, item):
        return self.config[item]

    # TODO save
