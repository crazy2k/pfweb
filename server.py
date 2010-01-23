
import xmlrpclib

conn = xmlrpclib.ServerProxy("http://localhost:8027")


#
# Public functions
#

def get_universities():
    return conn.get_universidades()

def get_faculties(uni = ''):
    return conn.get_facultades(uni)

def get_programs(uni = '', fac = ''):
    return conn.get_carreras(uni, fac)

def get_areas(carrera):
    return conn.get_areas(carrera)

def get_materias(carrera, area):
    return conn.get_materias(carrera, area)

def get_correlativas(carrera, materia):
    return conn.get_correlativas(carrera, materia)

def get_info_materia(carrera, materia):
    return conn.get_info_materia(carrera, materia)

def register(user, passwd):
    return conn.register(user, passwd)



#
# Private functions (per user)
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


def data_3tuple(uni = '', fac = '', itemized = False):
    """Returns a 3-tuple which contains three dictionaries (itemized
    if required) with the results of get_universities(),
    get_faculties() and get_programs(), passing them the given
    parameters.

    """

    unis = get_universities()
    if not uni:
        uni = unis.keys()[0]

    facs = get_faculties(uni)
    if not fac:
        fac = facs.keys()[0].split('/')[-1]

    carrs = get_programs(uni, fac)

    t = (unis, facs, carrs)
    if itemized:
        t = tuple(d.items() for d in t)

    return t
