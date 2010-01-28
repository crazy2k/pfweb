
import os

import web

import config
import server
import utils


render_in_context = web.template.render('templates/', base = 'layout')
render = web.template.render('templates/')


#
# Special purpose pages
#

class static:
    def GET(self):
        """By doing GET <URL for this page>?file=<file>, if the file
        <file> is in the directory specified by config.static_dir, then
        its content is returned.

        The standard way to do this is by placing the files in a
        static/ directory placed where the script that runs the web.py
        server is, and serving the files statically. However, that
        seems to work with WSGI but not with CGI mode. This sould be
        more portable.
        
        """
        i = web.input()

        fpath = os.path.join(config.static_dir, i.file)
        if os.path.isfile(fpath):

            # We choose the content-type by looking at the file's
            # extension. The mimetypes module could be used instead,
            # but doing it by hand gives us the flexibility to choose
            # what is most portable.
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

        else:
            return web.notfound()


class pieces:
    def GET(self):
        i = web.input()

        avl_funcs = ['facslist', 'progslist', 'progdata',
            'progtab']

        if i.func in avl_funcs:
            # save requested function
            f = getattr(pieces, i.func)

            # clean the storage (so it doesn't have the function's name
            # anymore)
            del i.func

            # call the function
            return f(**i)

        else:
            return web.notfound()

    @classmethod
    def facslist(cls, uni):
        facs = server.get_faculties(uni).items()
        return render._options_fac(facs)

    @classmethod
    def progslist(cls, uni, fac):
        carrs = server.get_programs(uni, fac).items()
        return render._options_prog(carrs)

    @classmethod
    def progdata(cls, num = 1, id = '', inid = '', inim = '', iniy = '',
        uni = '', fac = '', prog = ''):

        unis, facs, carrs = server.data_3tuple(uni, fac, itemized = True)

        uni_options = render._options_uni(unis, selected = uni)
        fac_options = render._options_fac(facs, selected = fac)
        carr_options = render._options_prog(carrs, selected = prog)

        return render._progdata(num, id, inid, inim, iniy, uni_options,
            fac_options, carr_options)
    
    @classmethod
    def progtab(cls, num):
        return render._progtab(num)


#
# Ordinary pages
#

class register:
    def GET(self):
        progdata = pieces.progdata()
        return render_in_context.register(progdatas = [progdata])

    def POST(self):
        i = web.input('username', 'passwd', 'realname')
        i = utils.unflatten(i, '/')

        class RegistrationError(Exception):
            def __init__(self, err):
                self.err = err

        try:
            err = server.register(i.username, i.passwd)

            # (0, <anything>) means success
            if err[0] != 0:
                raise RegistrationError(err)

            # user is registered; now its personal info is set
            sid = server.auth(i.username, i.passwd)

            personal = server.get_personal(sid)
            personal['realname'] = i.realname

            personal['progdatas'] = []
            for progdata in i.progdatas.itervalues():
                pd_dict = {
                    'id': progdata.padron,
                    'uni': progdata.uni,
                    'fac': progdata.fac,
                    'prog': progdata.carr,
                    'inid': progdata.inid,
                    'inim': progdata.inim,
                    'iniy': progdata.iniy,
                }
                personal['progdatas'].append(pd_dict)

            print 'ha'

            ret = server.set_personal(sid, personal)
            # error handling
            if ret[0] != 0:
                if ret[0] == 3 or ret[0] == 4:
                    print ret
                    err = (3, 'Registration succeeded but some data' +
                        ' wasn\'t saved.')
                else:
                    err = ret
                print ret
                raise RegistrationError(err)

            return render_in_context.register_ok(i.username)
        
        except RegistrationError as e:
            # regenerate user's input
            progdatas = []
            for num, progdata in i.progdatas.iteritems():
                html = pieces.progdata(num, id = progdata.padron,
                    uni = progdata.uni, fac = progdata.fac,
                    prog = progdata.carr, inid = progdata.inid,
                    inim = progdata.inim, iniy = progdata.iniy)
                progdatas.append(html)

            # passwd intentionally left blank
            return render_in_context.register(e.err, i.username, '',
                i.realname, progdatas)


class login:
    def GET(self):
        i = web.input(failed = 0, register_ok = 0)
        return render_in_context.login(failed = i.failed,
            register_ok = i.register_ok)


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
        user = utils.filterstr(i.user).lower()
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
        carrera_desc = server.get_programs()[personal['carrera']]
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

        new = utils.filterstr(i.new1)

        server.set_passwd(sid, new)
        raise web.seeother('chpasswd?action_ok=1')


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
        carrera_desc = server.get_programs()[personal['carrera']]
        mat_dict = server.get_materias(personal['carrera'], '')
        mat_list = mat_dict.keys()
        mat_list.sort()

        materias = []
        for cod in mat_list:
            info = server.get_info_materia(carrera, cod)
            materias.append(info)

        return render_in_context.listamaterias(carrera_desc = carrera_desc,
            materias = materias, personal = personal, mat_dict = mat_dict)


