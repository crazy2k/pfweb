#!/usr/bin/python

import web

import config
import pages


root = config.root

urls = (
    root,                       'pages.login',
    root + '/',                 'pages.login',
    root + '/login',            'pages.login',
    root + '/register',         'pages.register',
    root + '/index',            'pages.index',
    root + '/account',          'pages.account',

    root + '/logout',           'pages.logout',
    root + '/setmateria',       'pages.setmateria',
    root + '/cursandomateria',  'pages.cursandomateria',
    root + '/corregirnota',     'pages.corregirnota',
    root + '/datosmateria',     'pages.datosmateria',
    root + '/listamaterias',    'pages.listamaterias',
    root + '/personal',         'pages.personal',
    root + '/chpasswd',         'pages.chpasswd',
    root + '/mainhelp',         'pages.mainhelp',

    root + '/pieces',           'pages.pieces',

    root + '/static',           'pages.static',
)

web.internalerror = web.debugerror

if __name__ == "__main__":
    app = web.application(urls)
    app.run()

