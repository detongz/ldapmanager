import ConfigParser
import os

config = ConfigParser.RawConfigParser()
path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config/server.conf")
config.read(path)

def get_configs(section):
    conf = {}
    for item in config.items(section):
        conf[item[0]] = item[1]
    return conf

if __name__ == '__main__':
    print(get_configs('ldap'))
