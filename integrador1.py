import socket
import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
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
		print('[%s - Registrar libacion] Sin Internet .. enviando a archivo plano ...',str(fecha))
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

def cargar_libaciones_offline():
	with open(_libacion,"r+") as libac_file: 
		libaciones = libac_file.readlines()
		offline = []

		if not libaciones:
			return False

		for libacion in libaciones:
			data = libacion.rstrip().split('|')
			flor = data[0]
			fecha = datetime.strptime(data[1], "%Y-%m-%d %H:%M:%S")
			# Ajuste a UTC
			# fecha = fecha + timedelta(hours=5)
			f = fecha.strftime("%Y-%m-%d %H:%M:%S")
			vals = { 'flor' :  flor , 'fecha' : f }
			if internet():
				libacion_mqqt(vals)
			else:
				# identificar los offline de nuevo y borrar los correctos
				offline.append(libacion)
		if offline:
			# Limpiar archivo ( quitar los exitosos)
			# libac_file.seek(0)
			libac_file.truncate(0)
			libac_file.writelines(offline)
			libac_file.close()
		else:
			libac_file.truncate(0)
			libac_file.close()

def cargar_clima_offline():
	with open(_clima,"r+") as clima_file: 
		clima = clima_file.readlines()
		offline = []      

		if not clima:
			return False

		for c in clima:
			data = c.rstrip().split('|')
			fecha_raw = data[0]
			dir_viento = data[1]
			vel1_viento = data[2]
			vel5_viento = data[3]
			lluvia1 = data[4]
			lluvia24 = data[5]
			temp = data[6]
			hum = data[7]
			pres_adm = data[8]
			co2 = data[9] or ''
			voc = data[10] or ''

			vals = {
				'fecha' : fecha_raw, 'dir' : dir_viento, 
				'speed1' : vel1_viento, 'speed5' : vel5_viento, 
				'hour1' : lluvia1, 'hour24' : lluvia24, 
				'temp' : temp, 'hum' : hum, 
				'bp' : pres_adm, 'co2' : co2, 
				'voc' : voc             
			}

			if internet():
				clima_mqqt(json.dumps(vals))
			else:
				# TODO: identificar los offline de nuevo y borrar los correctos
				offline.append(c)
		if offline:
			# Limpiar archivo ( quitar los exitosos)
			# libac_file.seek(0)
			clima_file.truncate(0)
			clima_file.writelines(offline)
			clima_file.close()
		else:
			clima_file.truncate(0)
			clima_file.close()			

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

	fecha = datetime.strptime(fecha_raw, "%a %b %e %H:%M:%S %Y")
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
GPIO.add_event_detect(21, GPIO.BOTH, callback = evt_flor3 , bouncetime=500)
GPIO.add_event_detect(22, GPIO.BOTH, callback = evt_flor4 , bouncetime=500)

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

def integrador():
	print('[UQ] Iniciando Estacion Climatica')
	while True:
		# Comprobar si es la hora de verificar datos offline    
		liberar_offline()
				
		arduino_input = ser.readline()
		print(arduino_input)
		if internet():
			clima_mqqt(arduino_input)
		else:
			print('[Leer Clima] Sin Internet .. enviando a archivo plano ...')
			clima_offline(arduino_input)
		


def liberar_offline():
	'Intentar cargar datos offline cuando se restaure la conexion a internet'
	ahora = datetime.now()
	print('Comprobar para cargar offline ... ', str(ahora))
	if ahora.hour == 23 and ahora.minute < 05:
		print('Cargando datos offline')
		cargar_clima_offline()
		cargar_libaciones_offline()

integrador()
