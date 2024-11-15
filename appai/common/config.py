import json
import os
import pprint
import logzero
from logzero import logger 
from pathlib import Path

class Config:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, "r") as f:
            self.jfile = json.load(f)    
    
    def getv(self, name):
        return self.jfile[name]
    
    def setv(self, name, value):
        self.jfile[name] = value

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.jfile, f, indent=4)
    def json(self):
        return self.jfile
    def show(self):
        pprint.pprint(self.jfile)

def ConfigInit():
    logzero.logfile(os.getcwd() + "loomaai.log")
    home = str(Path.home())
    logger.info("HOME: " + str(Path.home()))
    filename = home + "/.config/loomaai/config.json"
    logger.info("Config file: " + filename)
    cfg = Config(filename)
    logger.debug("loomaai initialized")
    return cfg
