import RPi.GPIO as GPIO
import time
import requests
import json

TransistortPin = 16    # pin for transistor control
TempGreen = 20         # pin for green temp LED
TempRed = 21           # pin for red temp LED
WGreen = 13
WRed = 19
WYellow = 26

GPIO.cleanup() #Clean up pinouts

GPIO.setmode(GPIO.BCM) #set pinout hanling based on GPIO NR
GPIO.setup([TransistortPin, TempGreen, TempRed, WGreen, WRed, WYellow], GPIO.OUT)

# Set pins to high(+3.3V)
GPIO.output(TransistortPin, GPIO.HIGH)
GPIO.output(TempRed, GPIO.HIGH)
GPIO.output(TempGreen, GPIO.HIGH)
GPIO.output(WGreen, GPIO.HIGH)
GPIO.output(WYellow, GPIO.HIGH)
GPIO.output(WRed, GPIO.HIGH)

try:
    while True:
        #Request newest data from server
        wResponse = requests.get('http://46.101.118.225:7331/W/WReaction/5')
        thResponse = requests.get('http://46.101.118.225:7331/TH/THReaction/5')
        #Format respnse to json
        w_json_data = json.loads(wResponse.text)
        th_json_data = json.loads(thResponse.text)
        #print json response
        print "weight response: "+w_json_data
        print "temp / hum response: " + th_json_data

        #Handle LEDS for temp
        if th_json_data['temperature'] > 22:
            GPIO.output(TempRed, GPIO.LOW)  # led on
            GPIO.output(TempGreen, GPIO.HIGH) # led off
        else:
            GPIO.output(TempRed, GPIO.HIGH)  # led on
            GPIO.output(TempGreen, GPIO.LOW)  # led off

        # Handle fan for HUM
        if th_json_data['humidity'] < 30:
            GPIO.output(TransistortPin, GPIO.LOW)  # fan off
        else:
            GPIO.output(TransistortPin, GPIO.HIGH)  # fan on

        optimum = 1.3 * 1000
        max = optimum * 1.05
        min = optimum * 0.95
        currentMeasure = float(w_json_data['distance']) * 1000

        if currentMeasure > min and currentMeasure < max:
            GPIO.output(WGreen, GPIO.HIGH)
            GPIO.output(WRed, GPIO.LOW)  # led on
            GPIO.output(WYellow, GPIO.LOW)  # led off
        elif currentMeasure < max:
            GPIO.output(WRed, GPIO.LOW)  # led on
            GPIO.output(WGreen, GPIO.HIGH)  # led off
            GPIO.output(WGreen, GPIO.LOW)
        else:
            GPIO.output(WRed, GPIO.HIGH)  # led on
            GPIO.output(WGreen, GPIO.LOW)  # led off
            GPIO.output(WYellow, GPIO.LOW)

        time.sleep(5)

except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed
    print 'Closing...'
    GPIO.cleanup()