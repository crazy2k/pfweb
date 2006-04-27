
import xmlrpclib

conn = xmlrpclib.ServerProxy("http://localhost:8027")


#
# Funciones publicas
#

def get_carreras():
	return conn.get_carreras()

def get_areas(carrera):
	return conn.get_areas(carrera)

def get_materias(carrera, area):
	return conn.get_materias(carrera, area)

def get_correlativas(carrera, materia):
	return conn.get_correlativas(carrera, materia)

def register(user, passwd):
	return conn.register(user, passwd)



#
# Funciones privadas (por usuario)
#

def auth(user, passwd):
	return conn.auth(user, passwd)

def get_personal(sid):
	return conn.get_personal(sid)

def set_personal(sid, dic):
	return conn.set_personal(sid, dic)

def set_passwd(sid, passwd):
	return conn.set_passwd(sid, passwd)

def get_estado_materia(sid, materia):
	return conn.get_estado_materia(sid, materia)

def set_estado_materia(sid, materia, estado):
	return conn.set_estado_materia(sid, materia, estado)

def get_aprobadas(sid):
	return conn.get_aprobadas(sid)

def get_cursando(sid):
	return conn.get_cursando(sid)

def get_para_cursar(sid):
	return conn.get_para_cursar(sid)


