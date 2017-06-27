import RPi.GPIO as GPIO
import time
import requests
import json

HumGreen = 20
HumRed = 21
HumYellow = 16

GPIO.setmode(GPIO.BCM)

time.sleep(1)

GPIO.setup([HumRed, HumGreen, HumYellow], GPIO.OUT)

GPIO.output(HumRed, GPIO.HIGH)
GPIO.output(HumGreen, GPIO.HIGH)
GPIO.output(HumYellow, GPIO.HIGH)

try:
    while True:
        r = requests.get('http://46.101.118.225:7331/W/WReaction/5')
        json_data = json.loads(r.text)
        print json_data['distance']

        GPIO.output(HumRed, GPIO.HIGH)
        GPIO.output(HumGreen, GPIO.HIGH)
        GPIO.output(HumYellow, GPIO.HIGH)

        optimum = 1.3*1000
        max = optimum*1.05
        min = optimum*0.95
        currentMeasure = float(json_data['distance'])*1000

        if currentMeasure > min and currentMeasure < max:
            GPIO.output(HumGreen, GPIO.HIGH)
            GPIO.output(HumRed, GPIO.LOW)  # led on
            GPIO.output(HumYellow, GPIO.LOW)  # led off
        elif currentMeasure < max:
            GPIO.output(HumRed, GPIO.LOW)  # led on
            GPIO.output(HumGreen, GPIO.HIGH) # led off
            GPIO.output(HumGreen, GPIO.LOW)
        else:
            GPIO.output(HumRed, GPIO.HIGH)  # led on
            GPIO.output(HumGreen, GPIO.LOW)  # led off
            GPIO.output(HumYellow, GPIO.LOW)

        time.sleep(2)
except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed.
    GPIO.output(HumRed, GPIO.HIGH)
    GPIO.output(HumGreen, GPIO.HIGH)
    GPIO.cleanup()

