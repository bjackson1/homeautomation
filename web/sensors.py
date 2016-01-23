import networking
import time
from storage import redisclient


class temperaturesensor:
    def __init__(self, id, config):
        self.id = id
        self.hardwareid = config['hardwareid']
        self.name = config['name']
        self.host = config['host']
        self.islocal = networking.addressislocal(self.host)

        if self.islocal:
            self.reader = temperaturesensorreader(self.hardwareid)

    def get(self):
        return redisclient.getasstring(self.id)

    def update(self):
        if self.islocal:
            temp = self.reader.get()
            redisclient.set(self.id, temp)
            return temp

        return None


class temperaturesensorreader:
    def __init__(self, sensorid):
        self.location = '/sys/bus/w1/devices/' + sensorid + '/w1_slave'

    def get(self):
        datafile = open(self.location)
        data = datafile.read()
        datafile.close()
        tempdata = data.split("\n")[1].split(" ")[9]
        temp = float(tempdata[2:])
        temp = temp / 1000

        return temp
