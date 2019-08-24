import RPi.GPIO as GPIO

cargar_codigo = False

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11,GPIO.OUT)

GPIO.output(11, cargar_codigo)

print('Ejecutado ...');
