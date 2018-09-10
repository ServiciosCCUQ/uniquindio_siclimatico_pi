import random
import time
import odoorpc

odoo = odoorpc.ODOO('206.189.172.62', port=8069)

print('Listado Bases de datos %s' , odoo.db.list())

odoo.login('sic', 'admin', '123')

# Current user
user = odoo.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company

#Acceso al modelo de datos
medicion = odoo.env['uniquindio.medicion']



while True:
	precipitacion = random.randint(100, 200)
	humedad_amb = random.randint(20, 80)
	temp = random.randint(-10, 50)
	humedad = random.randint(10, 100)

	medicion.create({'estacion_id':1,'tipo_id':1 , 'valor': humedad , 'unidad': '%'})
	medicion.create({'estacion_id':1,'tipo_id':2 , 'valor': temp , 'unidad': 'Grados Centigrados'})
	medicion.create({'estacion_id':1,'tipo_id':3 , 'valor': humedad_amb , 'unidad': '%'})
	medicion.create({'estacion_id':1,'tipo_id':4 , 'valor': precipitacion , 'unidad': 'cm3'})
	time.sleep(30)