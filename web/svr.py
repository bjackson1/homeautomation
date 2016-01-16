#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import render_template
from socket import gethostname
from threading import Thread

from hwcontrol import temperature, pins
import yaml
import urllib.request
import socket
import fcntl
import struct
import os
import time
import redis
import logging


SCRIPTPATH=os.path.dirname(os.path.realpath(__file__))
MOBILETMPL="main.mobile.html"


app = Flask(__name__)
#http = urllib.PoolManager()


def loadconfig():
  cfgstream = open(SCRIPTPATH + '/config.yaml')
  config = yaml.load(cfgstream)
  return config

def getfromurl(url):
  ret = ""

  try:
    with urllib.request.urlopen(url) as response:
      ret = response.read().decode('utf-8')
  except:
    print("Error retrieving from " + url)
    raise

  return ret

def putsetting(key, value):
  redisconnection.set(key, value)

def getsetting(key):
  return redisconnection.get(key)

@app.route('/temp/<room>')
def temp(room):
  config = loadconfig()
  try:
    temp = temperature().get(config['tempsensors'][room]['id']) 
    print ('Temperature reading: ' + str(temp))
  except:
    temp = "Unavailable"

  return render_template('temperature_bare', temperature=temp)

@app.route('/')
def alltemp():
  config = loadconfig()

  for room in config['tempsensors']:
    sensorcfg = config['tempsensors'][room]
    try:
      sensorcfg['reading'] = getsetting(room)
    except:
      sensorcfg['reading'] = "Unavailable"


  for control in config['controls']:
    controlconfig = config['controls'][control]

    host = controlconfig['host']
    try:
      controlstate = getcontrolstate(control)
    except:
      controlstate = "Unavailable"

    controlconfig['state'] = controlstate

  return render_template(MOBILETMPL, sensors=config['tempsensors'], controls=config['controls'])

@app.route('/gpio/<id>')
def getgpiostate(id):
  return str(pins().getpin(id))

@app.route('/gpio/<id>/<state>')
def setgpiostate(id, state):
  pins().setpin(id, state)
  return str(pins().getpin(id))

@app.route('/control/<control>')
def getcontrolstate(control):
  config = loadconfig()
  control = config['controls'][control]
  host = control['host']

  reversed = False
  if 'reversed' in control:
    reversed = True

  state = "Unknown"

  stateurl = 'http://' + host + ':5000/gpio/' + str(control['gpio'])
  try:
    state = getfromurl(stateurl)
  except:
    raise

  if reversed == True:
    if state == '1':
      state = '0'
    else:
      state = '1'

  return state

@app.route('/control/<controlname>/<state>')
def setcontrolstate(controlname, state):
  config = loadconfig()
  control = config['controls'][controlname]
  host = control['host']

  if 'statusgpio' in control:
    statusledurl = 'http://' + host + ':5000/gpio/' + str(control['statusgpio']) + '/' + state
    getfromurl(statusledurl)

  if 'dependsupon' in control: # and state == 'on':
    setcontrolstate(control['dependsupon'], state)


  reversed = False
  if 'reversed' in control:
    reversed = True
    state = 'off' if state == 'on' else 'on'

  stateurl = 'http://' + host + ':5000/gpio/' + str(control['gpio']) + '/' + state
  newstate = getfromurl(stateurl)

  if reversed == True:
    newstate = '0' if newstate == '1' else '1'

  putsetting(controlname, newstate)

  return newstate

@app.route('/togglecontrol/<control>')
def togglecontrol(control):
  currentstate = getcontrolstate(control)
  newstate = 'on' if currentstate == '0' else 'off'
  setcontrolstate(control, newstate)
  return newstate


def switchworker(gpioid, control):
  gpio.setmode(gpio.BCM)
  gpio.setup(gpioid, gpio.IN)

  while True:
    gpio.wait_for_edge(gpioid, gpio.FALLING)
    print ("Button " + str(gpioid) + " for " + control + " pressed")
    togglecontrol(control)
    time.sleep(0.25)

  return True


def createswitchworkers():
  config = loadconfig()
  gpio.setmode(gpio.BCM)

  switches = config['switches']

  if gethostname() in switches['hosts']:
    hostswitches = switches['hosts'][gethostname()]
    for sw in hostswitches:
      t = Thread(target = switchworker, args = (hostswitches[sw]['gpio'], hostswitches[sw]['control']))
      t.start()
      print ("Switch worker thread started for " + hostswitches[sw]['control'])


def temperatureworker():
  while True:
    print("Getting temperatures...")
    config = loadconfig()

    for room in config['tempsensors']:
      sensorcfg = config['tempsensors'][room]
  
      host = sensorcfg['host']
      friendlyname = sensorcfg['friendlyname']
      sensorid = sensorcfg['id']
      try:
        tempreading = getfromurl('http://' + host + ':5000/temp/' + room) #urllib.urlopen('http://' + host + ':5000/temp/' + room).read()
      except:
        tempreading = "Unavailable"

      #print("type=Temperature, sensor=" + room + ", reading=" + tempreading)
      logging.info("type=Temperature, sensor=" + room + ", reading=" + tempreading)
      putsetting(room, tempreading)

    time.sleep(60)

def createtemperatureworker():
  t = Thread(target=temperatureworker)
  t.start()
  print ("Temperature worker thread started")

redisconnection = redis.StrictRedis(host=loadconfig()['services']['redis']['host'], port=loadconfig()['services']['redis']['port'], db=0)
logging.basicConfig(filename='/var/log/hasvr.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H.%M.%S')

logging.info('started')

if __name__ == '__main__':
#  createswitchworkers()
  createtemperatureworker()
  app.run(debug=True, host='0.0.0.0', threaded=True)

