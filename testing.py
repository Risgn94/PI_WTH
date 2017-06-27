import threading
import time
import RPi.GPIO as GPIO
import requests
import datetime
import json

def timer(name, delay, repeat):
    print  "\r\nTimer: ", name, " Started"

    print "\r\n", name, " has the acquired the lock"
    while repeat > 0:
        time.sleep(delay)
        print "\r\n", name, ": ", str(time.ctime(time.time()))
        repeat -= 1

    print "\r\n", name, " is releaseing the lock"

    print "\r\nTimer: ", name, " Completed"

def tempHum(channel, j, data):
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

def proxyDef(channel, j, data):
    tempHum(channel, j, data)

def Main():
    channel = 18
    data = []
    j = 0

    GPIO.setmode(GPIO.BCM)

    time.sleep(1)

    GPIO.setup(channel, GPIO.OUT)

    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(channel, GPIO.HIGH)

    GPIO.setup(channel, GPIO.IN)

    t1 = threading.Thread(target=timer, args=("Timer1", 2, 5))
    t2 = threading.Thread(target=proxyDef, args=(channel, j, data))

    t1.start()
    t2.start()

    print "\r\nMain Complete"

if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed
        print 'Closing...'
        GPIO.cleanup()