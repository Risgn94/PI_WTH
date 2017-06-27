import RPi.GPIO as GPIO
import time
import requests
import json
import datetime
import threading

TransistorPin = 21  # pin for transistor control
TempGreen = 20  # pin for green temp LED
TempRed = 16  # pin for red temp LED
WGreen = 13
WRed = 19
WYellow = 26
channel = 18
data = []
j = 0

channels_used = [21, 20, 16, 13, 19, 26, 18]

def tempHum():
	while GPIO.input(channel) == GPIO.LOW:
		continue

	while GPIO.input(channel) == GPIO.HIGH:
		continue

	while j < 40:
		k = 0
		while GPIO.input(channel) == GPIO.LOW:
			continue

		while GPIO.input(channel) == GPIO.HIGH:
			k += 1
			if k > 100:
				break

		if k < 8:
			data.append(0)
		else:
			data.append(1)

		j += 1

	print "sensor is working."
	#print data

	humidity_bit = data[0:8]
	humidity_point_bit = data[8:16]
	temperature_bit = data[16:24]
	temperature_point_bit = data[24:32]
	check_bit = data[32:40]

	humidity = 0
	humidity_point = 0
	temperature = 0
	temperature_point = 0
	check = 0

	for i in range(8):
		humidity += humidity_bit[i] * 2 ** (7 - i)
		humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
		temperature += temperature_bit[i] * 2 ** (7 - i)
		temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
		check += check_bit[i] * 2 ** (7 - i)

	tmp = humidity + humidity_point + temperature + temperature_point

	if check == tmp:
		print "temperature : ", temperature, ", humidity : " , humidity
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		r = requests.post('http://46.101.118.225:7331/TH/THData', data = {'id': 5, 'humidity': humidity, 'temperature': temperature, 'timestamp': st})
		json_data = json.loads(r.text)
		#print json_data['message']
	else:
		print "wrong"
		print "temperature : ", temperature, ", humidity : " , humidity, " check : ", check, " tmp : ", tmp
def ledHandling():
    while True:
        tempHum()
        #Request newest data from server
        wResponse = requests.get('http://46.101.118.225:7331/W/WReaction/5')
        thResponse = requests.get('http://46.101.118.225:7331/TH/THReaction/5')
        #Format respnse to json
        w_json_data = json.loads(wResponse.text)
        th_json_data = json.loads(thResponse.text)
        #print json response
        print "Server Responses:"
        print "Attribute      | Value"
        print "___________________________"
        print "Distance:      |"+str(w_json_data['distance'])
        print "___________________________"
        print "Temperature:   |"+str(th_json_data['temperature'])
        print "Humidity:      |"+str(th_json_data['humidity'])
        print "___________________________"
        print "\n"

        #Handle LEDS for temp
        if th_json_data['temperature'] > 22:
            GPIO.output(TempRed, GPIO.LOW)  # led on
            GPIO.output(TempGreen, GPIO.HIGH) # led off
        else:
            GPIO.output(TempRed, GPIO.HIGH)  # led on
            GPIO.output(TempGreen, GPIO.LOW)  # led off

        # Handle fan for HUM
        if th_json_data['humidity'] < 30:
            GPIO.output(TransistorPin, GPIO.LOW)  # fan off
        else:
            GPIO.output(TransistorPin, GPIO.HIGH)  # fan on

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

def timer(name, delay, repeat):
    print  "\r\nTimer: ", name, " Started"
    print "\r\n", name, " has the acquired the lock"
    while repeat > 0:
        time.sleep(delay)
        print "\r\n", name, ": ", str(time.ctime(time.time()))
        repeat -= 1

    print "\r\n", name, " is releaseing the lock"
    print "\r\nTimer: ", name, " Completed"

def Main():
    t1 = threading.Thread(target=tempHum)
    t2 = threading.Thread(target=ledHandling)
    t3 = threading.Thread(target=timer, args=("Timer3", 4, 5))

    t1.start()
    t2.start()
    t3.start()

    print "\r\nMain Complete"

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)  # set pinout hanling based on GPIO NR

        time.sleep(1)

        GPIO.setup([TransistorPin, TempGreen, TempRed, WGreen, WRed, WYellow, channel], GPIO.OUT)

        # Hanlding tempRead
        GPIO.output(channel, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(channel, GPIO.HIGH)
        GPIO.setup(channel, GPIO.IN)

        # Set pins to high(+3.3V)
        GPIO.output(TransistorPin, GPIO.HIGH)
        GPIO.output(TempRed, GPIO.HIGH)
        GPIO.output(TempGreen, GPIO.HIGH)
        GPIO.output(WGreen, GPIO.HIGH)
        GPIO.output(WYellow, GPIO.HIGH)
        GPIO.output(WRed, GPIO.HIGH)

    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed
        print 'Closing...'
        for channel in channels_used:
            GPIO.cleanup(channel)


