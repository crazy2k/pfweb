#!/usr/bin/python

import web

import pages

# Site's root, necessary for some links.
# Don't touch ANYTHING else but this.
root = '/pf'

static_dir = 'static/'

urls = (
    root,                       'pages.login',
    root + '/',                 'pages.login',
    root + '/login',            'pages.login',
    root + '/auth',             'pages.auth',
    root + '/logout',           'pages.logout',
    root + '/index',            'pages.index',
    root + '/setmateria',       'pages.setmateria',
    root + '/cursandomateria',  'pages.cursandomateria',
    root + '/corregirnota',     'pages.corregirnota',
    root + '/datosmateria',     'pages.datosmateria',
    root + '/listamaterias',    'pages.listamaterias',
    root + '/personal',         'pages.personal',
    root + '/chpasswd',         'pages.chpasswd',
    root + '/register',         'pages.register',
    root + '/mainhelp',         'pages.mainhelp',

    root + '/pieces',           'pages.pieces',

    root + '/static',           'pages.static',
)

web.internalerror = web.debugerror

if __name__ == "__main__":
    app = web.application(urls)
    app.run()

