#!/usr/bin/env python3

import sys

sys.path.append('/var/www/homeautomation/web')

from flask import Flask
from flask import request
from flask import render_template
from threading import Thread

from controller import controller

import time
import logging


MOBILETMPL = "main.mobile.html"
application = Flask(__name__)
ctrl = controller()


@application.route('/')
def getdefault():
    temps = {}
    ctrls = {}

    for s in ctrl.sensors:
        temps[ctrl.sensors[s].id] = ctrl.sensors[s].get()

    for c in ctrl.controls:
        ctrls[ctrl.controls[c].id] = ctrl.controls[c].get()

    return render_template('main.html', temps=temps, ctrls=ctrls)


@application.route('/control/<id>')
def getcontrol(id):
    if id in ctrl.controls:
        return ctrl.controls[id].get()
    else:
        return 'unknown control'


@application.route('/control/<id>/<value>')
def setcontrol(id, value):
    if id in ctrl.controls:
        ct = ctrl.controls[id]
        ct.set(value)
        logging.info('Control=' + ct.id + ', Operation=set, value=' + value)

    return getcontrol(id)


@application.route('/sensor/<id>')
def getsensor(id):
    if id in ctrl.sensors:
        return ctrl.sensors[id].get()
    else:
        return 'unknown sensor'


@application.route('/logtemps')
def gettemps():
    ret = 'Logging readings...\n'

    for sensor in ctrl.sensors:
        output = ('Type=Temperature, sensor=' + sensor + ', reading=' + str(ctrl.sensors[sensor].get()))
        logging.info(output)

        ret = ret + output + '\n'

    return ret

logging.basicConfig(filename='/var/log/hasvr.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H.%M.%S')

logging.info('started')

if __name__ == '__main__':
    #ctrl = controller()
    application.run(debug=True, host='0.0.0.0', threaded=True)
