import ConfigParser

class Config(dict):
    pass

def read_config(config, section):
    parser = ConfigParser.ConfigParser()
    parser.read(config)
    res = Config()
    for param, value in parser.items(section):
        res[param] = value
        setattr(res, param, value)
    return res

