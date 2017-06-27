#! /usr/bin/python
import RPi.GPIO as GPIO
import time
import requests
import datetime
import json


def checkdist():
        GPIO.output(16, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(16, GPIO.LOW)
        while not GPIO.input(18):
                pass
        t1 = time.time()
        while GPIO.input(18):
                pass
        t2 = time.time()
        return (t2-t1)*340/2

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(18,GPIO.IN)
time.sleep(2)
try:
        while True:
		distanceVar = "%0.3f" %checkdist()
                print distanceVar
                time.sleep(0.5)
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                #46.101.118.225
		r = requests.post('http://46.101.118.225:7331/W/WData', data={'id': 1, 'distance': distanceVar, 'timestamp': st})
                json_data = json.loads(r.text)
                print json_data['message']
except KeyboardInterrupt:
        GPIO.cleanup()
