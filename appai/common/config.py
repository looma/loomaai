import json
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

    def show(self):
        pprint.pprint(self.jfile)

def ConfigInit():
    logzero.logfile("loomaai.log")
    #home = str(Path.home())
    #print(str(Path.home()) + " PATH HOME")
    #filename = home + "/.config/loomaai/config.json"
    cfg = Config("/Users/connorlee/Documents/GitHub/loomaai/config.json") #filename)
    logger.debug("LoomaAI initialized")
    return cfg

