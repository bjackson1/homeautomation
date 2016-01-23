#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import render_template
from threading import Thread

from controller import controller

import time
import logging


MOBILETMPL = "main.mobile.html"
app = Flask(__name__)
ctrl = controller()


@app.route('/')
def getdefault():
    return ctrl.sensors['test'].get()


@app.route('/control/<id>')
def getcontrol(id):
    if id in ctrl.controls:
        return ctrl.controls[id].name
    else:
        return 'unknown control'


@app.route('/control/<id>/<value>')
def setcontrol(id, value):
    if id in ctrl.controls:
        ct = ctrl.controls[id]
        logging.info('Control=' + ct.id + ', Operation=set, value=' + value)

    return getcontrol(id)


@app.route('/sensor/<id>')
def getsensor(id):
    if id in ctrl.sensors:
        return ctrl.sensors[id].get()
    else:
        return 'unknown sensor'


logging.basicConfig(filename='/var/log/hasvr.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H.%M.%S')

logging.info('started')

if __name__ == '__main__':
    #ctrl = controller()
    app.run(debug=True, host='0.0.0.0', threaded=True)
