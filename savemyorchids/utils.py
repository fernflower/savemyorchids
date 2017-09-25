import ConfigParser

CONFIG_FILE = "config"

class Config(dict):
    pass

def read_config(section, config=CONFIG_FILE):
    parser = ConfigParser.ConfigParser()
    parser.read(config)
    res = Config()
    for param, value in parser.items(section):
        res[param] = value
        setattr(res, param, value)
    return res

