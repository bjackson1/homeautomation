import RPi.GPIO as gpio


class temperature:

    def get(self, sensorid):
        try:
            dataFilePath = '/sys/bus/w1/devices/' + sensorid + '/w1_slave'
            datafile = open(dataFilePath)
            data = datafile.read()
            datafile.close()
            tempdata = data.split("\n")[1].split(" ")[9]
            temp = float(tempdata[2:])
            temp = temp / 1000
        except:
            temp = "Unavailable"

        return temp


class pins:

    def __init__(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)

    def getpin(self, id):
        gpionum = int(id)
        gpio.setup(gpionum, gpio.OUT)
        return gpio.input(gpionum)

    def setpin(self, id, state):
        try:
            gpionum = int(id)
            gpio.setup(gpionum, gpio.OUT)
            gpio.output(gpionum, True if state == 'on' else False)
            return True
        except:
            return False
