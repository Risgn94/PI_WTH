import RPi.GPIO as GPIO
import time
import requests
import json

HumGreen = 26
HumRed = 19
TempGreen = 13
TempRed = 6
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

time.sleep(1)

GPIO.setup([HumRed, HumGreen, TempGreen, TempRed], GPIO.OUT)

GPIO.output(HumRed, GPIO.HIGH)
GPIO.output(HumGreen, GPIO.HIGH)
GPIO.output(TempRed, GPIO.HIGH)
GPIO.output(TempGreen, GPIO.HIGH)
try:
    while True:
        r = requests.get('http://46.101.118.225:7331/TH/THReaction/5')
        json_data = json.loads(r.text)
        print json_data

	GPIO.output(HumRed, GPIO.HIGH)
	GPIO.output(HumGreen, GPIO.HIGH)
	GPIO.output(TempRed, GPIO.HIGH)
	GPIO.output(TempGreen, GPIO.HIGH)

        if json_data['temperature'] > 22:
            GPIO.output(TempRed, GPIO.LOW)  # led on
            GPIO.output(TempGreen, GPIO.HIGH) # led off
        else:
            GPIO.output(TempRed, GPIO.HIGH)  # led on
            GPIO.output(TempGreen, GPIO.LOW)  # led off

        if json_data['humidity'] < 30:
            GPIO.output(HumRed, GPIO.LOW)  # led on
            GPIO.output(HumGreen, GPIO.HIGH) # led off
        else:
            GPIO.output(HumRed, GPIO.HIGH)  # led on
            GPIO.output(HumGreen, GPIO.LOW)  # led off

        time.sleep(5)

except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed
    print 'Closing...'
    GPIO.output(HumRed, GPIO.HIGH)
    GPIO.output(HumGreen, GPIO.HIGH)
    GPIO.output(TempRed, GPIO.HIGH)
    GPIO.output(TempGreen, GPIO.HIGH)
    GPIO.cleanup()
