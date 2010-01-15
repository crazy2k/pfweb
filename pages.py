
import server
import web
import os

render_in_context = web.template.render('templates/', base = 'layout')
render = web.template.render('templates/')


#
# Funciones auxiliares
#

def filterstr(s):
	import string
	allowed = string.ascii_letters + string.digits
	new = [c for c in s if c in allowed]
	new = string.join(new, '')
	return new


#
# Paginas
#

class login:
	def GET(self):
		i = web.input(failed = 0, register_ok = 0)
		return render_in_context.login(failed = i.failed,
			register_ok = i.register_ok)


class static:
	def GET(self):
		"""Utilizando <base-URL>/static?file=<file>, si el archivo
		<file> se halla en el directorio definido en static_dir, se
		devuelve su contenido.
		
		"""
		# deberia estar en static/ y servirse estaticamente, pero como
		# es mas dificil de parametrizar dado que solo fuciona en modo
		# wsgi y no en modo cgi, lo ponemos aca por ahora pues es mas
		# portable
		i = web.input()

		static_dir = './static/'

		fpath = os.path.join(static_dir, i.file)
		if os.path.isfile(fpath):

			# elegimos el content-type en base a la extension;
			# podria usarse el modulo mimetypes, pero escribir los
			# tipos nosotros nos da la flexibilidad para elegir lo
			# mas portable
			ext = os.path.splitext(fpath)[1]
			if ext == '.css':
				ctype = 'text/css'
			elif ext == '.js':
				ctype = 'text/javascript'
			else:
				ctype = 'text/plain'

			web.header('Content-type', ctype)

			fd = open(fpath)
			content = fd.read()
			fd.close()

			return content


class mainhelp:
	def GET(self):
		sid = web.cookies(sid = None)['sid']

		logged_in = False
		if sid:
			logged_in = True

		return render_in_context.mainhelp(logged_in)

class auth:
	def POST(self):
		i = web.input('user', 'passwd')
		user = filterstr(i.user).lower()
		sid = server.auth(user, i.passwd)
		if not sid:
			raise web.seeother("login?failed=1")
		web.setcookie('sid', sid)
		raise web.seeother("index")


class logout:
	def GET(self):
		sid = web.cookies('sid')['sid']
		web.setcookie('sid', '')
		raise web.seeother("login")

class index:
	def GET(self):
		sid = web.cookies('sid')['sid']

		personal = server.get_personal(sid)
		inicio = personal['inicio']
		carrera_desc = server.get_carreras()[personal['carrera']]
		areas = server.get_areas(personal['carrera'])
		area_desc = areas[personal['area']]
		del areas

		cursando = server.get_cursando(sid).items()
		cursando.sort()

		para_cursar = server.get_para_cursar(sid).items()
		para_cursar.sort()

		apro_dict = server.get_aprobadas(sid)
		promedio = 0.0
		aprobadas = []
		for key in apro_dict:
			aprobadas.append([key] + apro_dict[key])
			promedio += apro_dict[key][0]
		if len(aprobadas):
			promedio = promedio / len(aprobadas)
		promedio = "%.2f" % promedio

		aprobadas.sort()

		creditos = 0
		for key in apro_dict:
			info = server.get_info_materia(personal['carrera'], key)
			creditos += info['creditos']

		cantaprobadas = len(aprobadas)

		return render_in_context.index(personal = personal,
			area_desc = area_desc, carrera_desc = carrera_desc,
			inicio = inicio, promedio = promedio, creditos = creditos,
			cantaprobadas = cantaprobadas, cursando = cursando,
			para_cursar = para_cursar, aprobadas = aprobadas)


class setmateria:
	def GET(self):
		sid = web.cookies('sid')['sid']

		# para cuando confirmamos que anduvo todo bien, se usa en el
		# template nomas
		i = web.input(action_ok = 0, cod = None)
		action_ok = i.action_ok
		cod = i.cod

		personal = server.get_personal(sid)
		matdict = server.get_materias(personal['carrera'], "")
		materias = matdict.items()
		materias.sort()
		aprobadas = server.get_aprobadas(sid)

		cursando = server.get_cursando(sid)
		curlist = cursando.keys()
		curlist.sort()

		return render_in_context.setmateria(action_ok = action_ok,
			cod = cod, matdict = matdict, materias = materias,
			aprobadas = aprobadas, curlist = curlist)

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input('cod', 'nota')

		ret = server.set_estado_materia(sid, i.cod, int(i.nota))
		if not ret:
			raise web.seeother('setmateria?action_ok=2')

		raise web.seeother('setmateria?action_ok=1;cod=%s' % i.cod)

class cursandomateria:
	def GET(self):
		sid = web.cookies('sid')['sid']

		i = web.input(action_ok = 0, cod = None)
		action_ok = i.action_ok
		cod = i.cod

		personal = server.get_personal(sid)
		matdict = server.get_materias(personal['carrera'], "")
		materias = matdict.items()
		materias.sort()
		aprobadas = server.get_aprobadas(sid)
		cursando = server.get_cursando(sid)
		curlist = cursando.keys()
		curlist.sort()

		return render_in_context.cursandomateria(action_ok, cod, matdict,
			materias, aprobadas, cursando)

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input('cod')

		ret = server.set_estado_materia(sid, i.cod, -1)
		if not ret:
			raise web.seeother('cursandomateria?action_ok=2')

		raise web.seeother('cursandomateria?action_ok=1;cod=%s' % i.cod)


class corregirnota:
	# es igual a setmateria, solo que con otro template

	def GET(self):
		sid = web.cookies('sid')['sid']

		i = web.input(action_ok = 0)
		action_ok = i.action_ok

		personal = server.get_personal(sid)
		aprobadas = server.get_aprobadas(sid)
		aplist = aprobadas.items()
		aplist.sort()
		cursando = server.get_cursando(sid)
		curlist = cursando.items()
		curlist.sort()

		return render_in_context.corregirnota(action_ok = action_ok,
			aplist = aplist, curlist = curlist)


	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input('cod', 'nota')

		ret = server.set_estado_materia(sid, i.cod, int(i.nota))
		if not ret:
			raise web.seeother('corregirnota?action_ok=2')
			
		raise web.seeother('corregirnota?action_ok=1')


class personal:
	def GET(self):
		sid = web.cookies('sid')['sid']

		i = web.input(action_ok = 0)
		action_ok = i.action_ok

		personal = server.get_personal(sid)

		areas = server.get_areas(personal['carrera']).items()

		return render_in_context.personal(action_ok = action_ok,
			personal = personal, areas = areas)

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input(nombre = '', padron = '', area = '')

		personal = server.get_personal(sid)
		personal['nombre'] = i.nombre
		personal['padron'] = i.padron
		if i.area:
			personal['area'] = i.area
		ret = server.set_personal(sid, personal)

		if not ret:
			raise web.seeother('personal?action_ok=2')

		raise web.seeother('personal?action_ok=1')


class chpasswd:
	def GET(self):
		sid = web.cookies('sid')['sid']
		i = web.input(action_ok = None)
		action_ok = i.action_ok
		return render_in_context.chpasswd(action_ok = action_ok)

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input("new1", "new2")

		if i.new1 != i.new2:
			raise web.seeother('chpasswd?action_ok=0')

		new = filterstr(i.new1)

		server.set_passwd(sid, new)
		raise web.seeother('chpasswd?action_ok=1')

class pieces:
	def GET(self):
		i = web.input()

		# guardar la funcion pedida
		f = getattr(pieces, i.func)

		# limpiar el storage (para que no tenga el nombre de
		# la funcion)
		del i.func

		# llamar a la funcion
		return f(**i)

	@classmethod
	def facslist(cls, uni):
		facs = server.get_facultades(uni).items()
		return render._facultad_options(facs)

	@classmethod
	def carrslist(cls, uni, fac):
		carrs = server.get_carreras(uni, fac).items()
		return render._carrera_options(carrs)

	@classmethod
	def datoscarrera(cls, num):
		unis, facs, carrs = data_3tuple(itemized = True)

		uni_options = render._universidad_options(unis)
		fac_options = render._facultad_options(facs)
		carr_options = render._carrera_options(carrs)

		return render._datoscarrera(num, uni_options,
			fac_options, carr_options)
	
	@classmethod
	def tabcarrera(cls, num):
		return render._tab_carrera(num)



def data_3tuple(uni = '', fac = '', itemized = False):

		unis = server.get_universidades()
		if not uni:
			uni = unis.keys()[0]

		facs = server.get_facultades(uni)
		if not fac:
			fac = facs.keys()[0].split('/')[-1]

		carrs = server.get_carreras(uni, fac)

		t = (unis, facs, carrs)
		if itemized:
			t = tuple(d.items() for d in t)

		return t

class register:
	def GET(self):
		i = web.input(error = 0, num = 1)

		datoscarrera = pieces.datoscarrera(i.num)
		return render_in_context.register(i.error, datoscarrera)

	def POST(self):
		i = web.input('username', 'passwd',
				nombre = '')

		username = filterstr(i.username)
		username = username.lower()
		passwd = filterstr(i.passwd)

		ret = server.register(username, passwd)
		if ret != 0:
			raise web.seeother('register?error=1')

		sid = server.auth(username, passwd)
		personal = server.get_personal(sid)
		personal['nombre'] = i.nombre
		personal['padron'] = i.padron
		personal['carrera'] = i.carrera
		personal['hace_tesis'] = 0
		personal['inicio'] = (int(i.inid), int(i.inim), int(i.iniy))
		personal['area'] = server.get_areas(i.carrera).keys()[0]
		ret = server.set_personal(sid, personal)
		if not ret:
			print personal
			print ret
			# XXX: (?) Ver que es esto...
			return
			raise web.seeother('register?error=2')

		raise web.seeother('login?register_ok=1')


class datosmateria:
	def GET(self):
		sid = web.cookies('sid')['sid']

		# si nos llaman con un codigo, entonces hacemos de cuenta que
		# es un POST (esto se usa para linkear de la lista de materias
		# a los datos de las materias
		i = web.input(cod = None)
		if i.cod:
			return self.POST()

		personal = server.get_personal(sid)
		materias = server.get_materias(personal['carrera'], '')
		materias = materias.items()
		materias.sort()

		return render_in_context.datosmateria(personal = personal,
			materias = materias)

	def POST(self):
		sid = web.cookies('sid')['sid']

		i = web.input('cod')
		codigo = i.cod

		personal = server.get_personal(sid)
		matdict = server.get_materias(personal['carrera'], '')

		carrera = personal['carrera']
		info = server.get_info_materia(carrera, codigo)
		info['dep'].sort()
		inmediatas = info['dep']
		inmediatas.sort()

		materias = matdict.items()
		materias.sort()

		correlativas = server.get_correlativas(carrera, codigo)
		correlativas = correlativas.keys()
		correlativas.sort()

		url = 'http://www.fi.uba.ar/guiaestudiante/pdf/%s.pdf' % \
				codigo.replace(".", "")

		return render_in_context.datosmateria(info = info,
			correlativas = correlativas, personal = personal,
			materias = materias, codigo = codigo,
			inmediatas = inmediatas, url = url, matdict = matdict) 


class listamaterias:
	def GET(self):
		# re ineficiente, hacemos un millon de lookups con el server

		sid = web.cookies('sid')['sid']
		personal = server.get_personal(sid)
		carrera = personal['carrera']
		carrera_desc = server.get_carreras()[personal['carrera']]
		mat_dict = server.get_materias(personal['carrera'], '')
		mat_list = mat_dict.keys()
		mat_list.sort()

		materias = []
		for cod in mat_list:
			info = server.get_info_materia(carrera, cod)
			materias.append(info)

		return render_in_context.listamaterias(carrera_desc = carrera_desc,
			materias = materias, personal = personal, mat_dict = mat_dict)


