from multiprocessing import Process
import socket
import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime
import json

import paho.mqtt.client as mqtt

# Configuracion Flores Libacion
flor1 = 0
flor2 = 0
flor3 = 0
flor4 = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(23,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22,GPIO.IN , pull_up_down=GPIO.PUD_DOWN)

# Arduino ( Estacion Climatica )
ser=serial.Serial("/dev/ttyACM0",9600)  #change ACM number as found from ls /dev/tty/ACM*
ser.baudrate=9600

# MQQT (Envio al Servidor)
broker_address = "ceam-csp.me" 
broker_port = 1883

_clima = 'clima.txt'
_libacion = 'libacion.txt'


def libacion_mqqt(vals):
	client = mqtt.Client("GreenStation") #create new instance
	client.connect(host=broker_address ,port=broker_port ) #connect to broker
	client.publish("libacion", json.dumps(vals) ) #publish

def libacion(flor):
	# TODO: Revisar si con el utcnow permite el manejo de la utc time.
	fecha = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	vals = { 'flor' :  flor , 'fecha' : fecha }
	if internet():
		libacion_mqqt(vals) 
	else:
		print('[Registrar libacion] Sin Internet .. enviando a archivo plano ...')
		libacion_offline(vals)

def libacion_offline(data):
	# TODO: Agregar Try/Except
	if not data:
		return False

	libac_file = open(_libacion,"a")
	flor = data.get('flor')
	fecha = data.get('fecha')
	libac_file.write("%s|%s\n" % (flor,fecha))
	libac_file.close()

def clima_offline(data):
	# TODO: Agregar Try/Except
	if not data:
		return False
	
	json_clima = json.loads(data)

	fecha_raw = json_clima.get('fecha')
	dir_viento = json_clima.get('dir')
	vel1_viento = json_clima.get('speed1')
	vel5_viento = json_clima.get('speed5')
	lluvia1 = json_clima.get('hour1')
	lluvia24 = json_clima.get('hour24')
	temp = json_clima.get('temp')
	hum = json_clima.get('hum')
	pres_adm = json_clima.get('bp')
	co2 = json_clima.get('co2') or ''
	voc = json_clima.get('voc') or ''

	fecha = datetime.strptime(fecha_raw, "%Y-%m-%dT%H:%M:%S")
	f = fecha.strftime("%Y-%m-%d %H:%M:%S")

	clima_file = open(_clima,"a")
	data_raw = (f, dir_viento, vel1_viento, vel5_viento, lluvia1, lluvia24, temp, hum, pres_adm, co2, voc)
	clima_file.write("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % data_raw)
	clima_file.close()


#Callbacks libacion
def evt_flor1(channel):
	print "evt_flor1 A: ", GPIO.input(channel)
	if GPIO.input(channel) == 0:
		libacion(flor=1)

def evt_flor2(channel):
	print "evt_flor2 B: ", GPIO.input(channel)
	if GPIO.input(channel) == 0:
		libacion(flor=2)

def evt_flor3(channel):
	print "evt_flor3 C: ", GPIO.input(channel)	
	if GPIO.input(channel) == 0:
		libacion(flor=3)

def evt_flor4(channel):
	print "evt_flor4 D: ", GPIO.input(channel)	
	if GPIO.input(channel) == 0:
		libacion(flor=4)
	

def testEvent(channel):	
	if GPIO.input(channel) == 0:
		libacion(flor=4)
		
	

#Interrupciones
GPIO.add_event_detect(23, GPIO.BOTH, callback = evt_flor1 , bouncetime=500)
GPIO.add_event_detect(24, GPIO.BOTH, callback = evt_flor2 , bouncetime=500)
GPIO.add_event_detect(21, GPIO.BOTH, callback = evt_flor3 , bouncetime=1000)
GPIO.add_event_detect(22, GPIO.BOTH, callback = evt_flor4 , bouncetime=1000)


print "flor4or A: ", flor1
print "flor4or B: ", flor2
print "flor4or C: ", flor3
print "flor4or D: ", flor4


def internet(host="8.8.8.8", port=53, timeout=3):
	'''
	Comprobar si Existe conexion a internet
	'''
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except socket.error as ex:
		print ex.message
		return False

def clima_mqqt(input):
	client = mqtt.Client("GreenStation") #create new instance
	client.connect(host=broker_address ,port=broker_port ) #connect to broker
	client.publish("clima", input ) #publish	

def leer_clima_serial():
	while True:
		try:
			time.sleep(1)
			arduino_input = ser.readline()
			
			if not arduino_input:
				continue
			
			print(arduino_input)
			if internet():
				clima_mqqt(arduino_input)
			else:
				print('[Leer Clima] Sin Internet .. enviando a archivo plano ...')
				clima_offline(arduino_input)		
		except Exception as e:
			print 'error serial',e
		
	
leer_clima_serial()
