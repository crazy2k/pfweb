
import server
import web


class login:
	def GET(self):
		i = web.input(failed = 0, register_ok = 0)
		failed = i.failed
		register_ok = i.register_ok
		web.render('login.html')


class style:
	def GET(self):
		# deberia estar en static/ y servirse estaticamente, pero como
		# es mas dificil de parametrizar dado que solo fuciona en modo
		# wsgi y no en modo cgi, lo ponemos aca por ahora pues es mas
		# portable
		web.render('style.css')


class auth:
	def POST(self):
		i = web.input('user', 'passwd')
		sid = server.auth(i.user, i.passwd)
		if not sid:
			return web.redirect("login?failed=1")
		web.setcookie('sid', sid)
		web.redirect("index")


class logout:
	def GET(self):
		sid = web.cookies('sid')['sid']
		web.setcookie('sid', '')
		web.redirect("login")

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

		creditos = 0
		for key in apro_dict:
			info = server.get_info_materia(personal['carrera'], key)
			creditos += info['creditos']

		cantaprobadas = len(aprobadas)

		web.render('index.html')


class setmateria:
	def GET(self):
		sid = web.cookies('sid')['sid']

		# para cuando confirmamos que anduvo todo bien, se usa en el
		# template nomas
		i = web.input(action_ok = 0)
		action_ok = i.action_ok

		personal = server.get_personal(sid)
		materias = server.get_materias(personal['carrera'], "")
		materias = materias.items()
		materias.sort()
		aprobadas = server.get_aprobadas(sid)

		web.render('setmateria.html')

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input('cod', 'nota')

		ret = server.set_estado_materia(sid, i.cod, int(i.nota))
		if not ret:
			return web.redirect('setmateria?action_ok=2')
		web.redirect('setmateria?action_ok=1')

class cursandomateria:
	def GET(self):
		sid = web.cookies('sid')['sid']

		i = web.input(action_ok = 0)
		action_ok = i.action_ok
		personal = server.get_personal(sid)
		materias = server.get_materias(personal['carrera'], "")
		materias = materias.items()
		materias.sort()
		aprobadas = server.get_aprobadas(sid)
		web.render('cursandomateria.html')

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input('cod')

		ret = server.set_estado_materia(sid, i.cod, -1)
		if not ret:
			return web.redirect('cursandomateria?action_ok=2')
		web.redirect('cursandomateria?action_ok=1')


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

		web.render('corregirnota.html')

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input('cod', 'nota')

		ret = server.set_estado_materia(sid, i.cod, int(i.nota))
		if not ret:
			return web.redirect('corregirnota?action_ok=2')
		web.redirect('corregirnota?action_ok=1')


class personal:
	def GET(self):
		sid = web.cookies('sid')['sid']

		i = web.input(action_ok = 0)
		action_ok = i.action_ok

		personal = server.get_personal(sid)

		areas = server.get_areas(personal['carrera']).items()

		web.render("personal.html")

	def POST(self):
		sid = web.cookies('sid')['sid']
		i = web.input(nombre = '', padron = '', area = '')

		personal = server.get_personal(sid)
		personal['nombre'] = i.nombre
		personal['padron'] = i.padron
		personal['area'] = i.area
		ret = server.set_personal(sid, personal)

		if not ret:
			return web.redirect('personal?action_ok=2')
		web.redirect('personal?action_ok=1')


class register:
	def GET(self):
		i = web.input(error = 0)
		error = i.error

		carreras = server.get_carreras().items()
		web.render("register.html")

	def POST(self):
		i = web.input('username', 'passwd', 'carrera',
				'inid', 'inim', 'iniy',
				nombre = '', padron = '')

		ret = server.register(i.username, i.passwd)
		if ret != 0:
			return web.redirect('register?error=1')

		sid = server.auth(i.username, i.passwd)
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
			return
			return web.redirect('register?error=2')
		web.redirect('login?register_ok=1')

class datosmateria:
	def GET(self):
		sid = web.cookies('sid')['sid']
		personal = server.get_personal(sid)
		materias = server.get_materias(personal['carrera'], '')
		materias = materias.items()
		materias.sort()

		# tienen valor en el POST, las seteamos a None para poder
		# usar condicionales en el template
		info = None
		correlativas = None

		web.render("datosmateria.html")

	def POST(self):
		sid = web.cookies('sid')['sid']

		i = web.input('cod')
		personal = server.get_personal(sid)
		materias = server.get_materias(personal['carrera'], '')

		carrera = personal['carrera']
		info = server.get_info_materia(carrera, i.cod)
		info['dep'].sort()
		inmediatas = [(mat, materias[mat]) for mat in info['dep']]
		inmediatas.sort()

		materias = materias.items()
		materias.sort()

		correlativas = server.get_correlativas(carrera, i.cod)
		correlativas = correlativas.items()
		correlativas.sort()

		web.render("datosmateria.html")


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

		web.render("listamaterias.html")


