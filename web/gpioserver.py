#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import render_template
from socket import gethostname
from threading import Thread

import RPi.GPIO as gpio
import yaml
import urllib2
import socket
import fcntl
import struct
import os
import time


SCRIPTPATH=os.path.dirname(os.path.realpath(__file__))
MOBILETMPL="main.mobile.html"

cfgstream = file(SCRIPTPATH + '/config.yaml')
config = yaml.load(cfgstream)

app = Flask(__name__)

@app.route('/temp/<room>')
def temp(room):
  dataFilePath = '/sys/bus/w1/devices/' + config['tempsensors'][room]['id'] + '/w1_slave'
  datafile = open(dataFilePath)
  data = datafile.read()
  datafile.close()

  tempdata = data.split("\n")[1].split(" ")[9]
  temp = float(tempdata[2:])
  temp = temp / 1000
  print 'Temperature reading: ' + str(temp)
  return render_template('temperature_bare', temperature=temp)

@app.route('/')
def alltemp():
  #room = 'understairs'

  for room in config['tempsensors']:
    sensorcfg = config['tempsensors'][room]

    host = sensorcfg['host']
    friendlyname = sensorcfg['friendlyname']
    sensorid = sensorcfg['id']
    tempreading = urllib2.urlopen('http://' + host + ':5000/temp/' + room).read()
    sensorcfg['reading'] = tempreading

    print tempreading

  for control in config['controls']:
    controlconfig = config['controls'][control]

    host = controlconfig['host']
    controlstate = getcontrolstate(control) #urllib2.urlopen('http://' + host + ':5000/gpio/' + str(controlconfig['gpio'])).read()
    controlconfig['state'] = controlstate

  return render_template(MOBILETMPL, sensors=config['tempsensors'], controls=config['controls'])

@app.route('/gpio/<id>')
def getgpiostate(id):
  gpio.setmode(gpio.BCM)

  gpionum = int(id)
  gpio.setup(gpionum, gpio.OUT)
  return str(gpio.input(gpionum))

@app.route('/gpio/<id>/<state>')
def setgpiostate(id, state):
  gpio.setmode(gpio.BCM)
  gpionum = int(id)
  gpio.setup(gpionum, gpio.OUT)
  gpio.output(gpionum, True if state == 'on' else False)
  return getgpiostate(id)
  

@app.route('/control/<control>')
def getcontrolstate(control):
  control = config['controls'][control]
  host = control['host']

  reversed = False
  if 'reversed' in control:
    reversed = True

  state = urllib2.urlopen('http://' + host + ':5000/gpio/' + str(control['gpio'])).read()

  if reversed == True:
    if state == '1':
      state = '0'
    else:
      state = '1'

  return state

@app.route('/control/<control>/<state>')
def setcontrolstate(control, state):
  control = config['controls'][control]
  host = control['host']

  if 'statusgpio' in control:
    urllib2.urlopen('http://' + host + ':5000/gpio/' + str(control['statusgpio']) + '/' + state)

  if 'dependsupon' in control: # and state == 'on':
    setcontrolstate(control['dependsupon'], state)

  print state

  reversed = False
  if 'reversed' in control:
    reversed = True
    if state == 'on':
      state = 'off'
    else:
      state = 'on'

  newstate = urllib2.urlopen('http://' + host + ':5000/gpio/' + str(control['gpio']) + '/' + state).read()

  if reversed == True:
    if newstate == '1':
      newstate = '0'
    else:
      newstate = '1'


  return newstate

@app.route('/togglecontrol/<control>')
def togglecontrol(control):
  currentstate = getcontrolstate(control)
  print currentstate
  if currentstate == '0':
    newstate = 'on'
  else:
    newstate = 'off'

  setnewstate = setcontrolstate(control, newstate)
  print setnewstate

  return newstate


def switchworker(gpioid, control):
  gpio.setmode(gpio.BCM)
  gpio.setup(gpioid, gpio.IN)

  while True:
    gpio.wait_for_edge(gpioid, gpio.FALLING)
    print "Button " + str(gpioid) + " for " + control + " pressed"
    togglecontrol(control)
    time.sleep(0.25)

  return True


def createswitchworkers():
  gpio.setmode(gpio.BCM)

  switches = config['switches']

  if gethostname() in switches['hosts']:
    hostswitches = switches['hosts'][gethostname()]
    for sw in hostswitches:
      t = Thread(target = switchworker, args = (hostswitches[sw]['gpio'], hostswitches[sw]['control']))
      t.start()
      print "Switch worker thread started for " + hostswitches[sw]['control']


if __name__ == '__main__':
  createswitchworkers()
  app.run(debug=True, host='0.0.0.0', threaded=True)

