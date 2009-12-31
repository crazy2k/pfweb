
import server
import web

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


class style:
	def GET(self):
		# deberia estar en static/ y servirse estaticamente, pero como
		# es mas dificil de parametrizar dado que solo fuciona en modo
		# wsgi y no en modo cgi, lo ponemos aca por ahora pues es mas
		# portable
		web.header('Content-type', 'text/css')
		return render.style()

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


class register:
	def GET(self):
		i = web.input(error = 0)

		carreras = server.get_carreras().items()
		return render_in_context.register(error = i.error,
			carreras = carreras)

	def POST(self):
		i = web.input('username', 'passwd', 'carrera',
				'inid', 'inim', 'iniy',
				nombre = '', padron = '')

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


