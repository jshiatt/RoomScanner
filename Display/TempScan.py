import os

def sensor():
	for i in os.listdir('/sys/bus/w1/devices'):
			if i != 'w1_bus_master1':
				probe = i
	return probe

def read(probe):
	location = '/sys/bus/w1/devices/' + probe + '/w1_slave'
	tfile = open(location)
	text = tfile.read()
	tfile.close()
	secondline = text.split("\n")[1]
	tempdata = secondline.split(" ")[9]
	temp = float(tempdata[2:])
	celsius = temp / 1000
	farenheit = (celsius * 1.8) + 32
	return farenheit

def loop(probe):
	while True:
		if read(probe) != None:
				print "Current indoor temperature: %0.3f F" % read(probe)

def kill():
	quit()

if __name__ == '__main__':
	try:
		serialNum = sensor()
		loop(serialNum)
	except KeybourdInterrupt:
		kill()
