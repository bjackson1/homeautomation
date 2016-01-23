from control import control
import sensors
from config import config
from threading import Thread
import time
import storage

class controller:

    def __init__(self):
        cfg = config().get()
        storage.redisclient(cfg['services']['redis']['host'], int(cfg['services']['redis']['port']))
        
        self.sensors = {}
        self.controls = {}
        self.reload()

        t = Thread(target=self.updateworker)
        t.start()


    def reload(self):
        cfg = config().get()
        # print(cfg['tempsensors'])

        for ts in cfg['tempsensors']:
            self.sensors[ts] = sensors.temperaturesensor(ts,
                cfg['tempsensors'][ts])

        for ct in cfg['controls']:
            self.controls[ct] = control(ct, cfg['controls'][ct])

    def update(self):
        for ts in self.sensors:
            self.sensors[ts].update()

    def updateworker(self):
        while True:
            try:
                self.update()
            except:
                print('Failed to update sensors')

            time.sleep(60)
