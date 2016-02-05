
import sys

sys.path.append('/var/www/homeautomation/web')

import yaml
import os


class config:
    SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        self.get()

    def get(self):
        cfgstream = open(self.SCRIPTPATH + '/config.yaml')
        self.current = yaml.load(cfgstream)
        return self.current
