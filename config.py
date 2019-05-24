from configparser import ConfigParser
import os

_configParser = None

def get_config():
    global _configParser
    if _configParser is None:
        _configParser = ConfigParser()
        configFilePath = os.path.join(os.getcwd(), 'config.ini')
        _configParser.read(configFilePath)
    return _configParser