
import sys

sys.path.append('/var/www/homeautomation/web')

import RPi.GPIO as gpio
import networking
import time
import request
from storage import redisclient


class control:

    def __init__(self, id, config):
        self.id = id
        self.name = config['name']
        self.host = config['host']
        self.controlpin = int(config['controlpin'])
        self.reversed = True if ('reversed' in config and str(
            config['reversed']).lower() == 'true') else False
        self.statuspin = int(config['statuspin']
                             ) if 'statuspin' in config else 0
        self.islocal = networking.addressislocal(self.host)

        if self.islocal:
            self.controlio = gpiocontrol(self.controlpin)

        if self.statuspin > 0:
            self.statusio = gpiocontrol(self.statuspin)

    def set(self, state):
        redisclient.set(self.id, state)

        if self.islocal:
            self.update()
        else:
            url = 'http://' + self.host + ':5000/control/' + self.id + '/' + state
            print('Passing control request to ' + url)
            request.getfromurl(url)

    def get(self):
        return redisclient.getasstring(self.id)

    def update(self):
        state = self.get()

        if state == 'on':
            controlpinstate = 1 if not self.reversed else 0
            statuspinstate = 1
        else:
            controlpinstate = 0 if not self.reversed else 1
            statuspinstate = 0

        self.controlio.set(controlpinstate)

        if self.statuspin > 0:
            self.statusio.set(statuspinstate)


class gpiocontrol:

    def __init__(self, pin):
        self.pin = int(pin)
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin, gpio.OUT)

    # def get(self):
    #   return gpio.input(self.pin)

    def set(self, state):
        gpio.output(self.pin, state)
