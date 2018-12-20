# -*- coding: utf-8 -*-
from __future__ import print_function # In python 2.7
import sys
import logging
import codificacion
#from flask import Flask, render_template, request, redirect, Response, jsonify
from flask import Flask, request #import main Flask class and request object
import random, json
import erppeek
import odoorpc


_logger = logging.getLogger(__name__)

app = Flask(__name__) #create the Flask app

@app.route('/recibirdatos')
def recibir_datos():
	req_data = request.args.get('raw')
	print(req_data, file=sys.stderr)
	if req_data:
		return procesar_raw(req_data)
	else:
		return 'no'
	



def procesar_raw(rawdata):
	odoo = odoorpc.ODOO('206.189.172.62', port=8069)
	odoo.login('sic', 'admin', '123')

	#Acceso al modelo de datos
	medicion = odoo.env['uniquindio.medicion']

	humedad_amb,temp,humedad,precipitacion = rawdata.split('|')

	print(humedad_amb, file=sys.stderr)
	print(temp, file=sys.stderr)
	print(humedad, file=sys.stderr)
	print(precipitacion, file=sys.stderr)

	medicion.create({'estacion_id':1,'tipo_id':1 , 'valor': humedad , 'unidad': '%'})
	medicion.create({'estacion_id':1,'tipo_id':2 , 'valor': temp , 'unidad': 'Grados Centigrados'})
	medicion.create({'estacion_id':1,'tipo_id':3 , 'valor': humedad_amb , 'unidad': '%'})
	medicion.create({'estacion_id':1,'tipo_id':4 , 'valor': precipitacion , 'unidad': 'cm3'})	

	return 'ok'


if __name__ == '__main__':
	#app.run("0.0.0.0", "5010")
	_logger.info('Arrancando Servidor ...')
	#print(codificacion.encode(KEY,'model:delphos.req.demof|id:1|instancia:fpaproduccion_oct_2017|campo:firma') , file=sys.stderr)
	#print(codificacion.decode(KEY,'vdDWpt6nydOd0aiho2CitdKgpdfa1NStyqRsYa6ZvtTmouDQzs9rx7CToKSftNbVpNvc082gxLSRYmJhh93Vot_d1KiXyrKfkQ==') , file=sys.stderr)
	app.run(host='0.0.0.0',debug=False, port=5050)
	#flask_log = Logging(app)