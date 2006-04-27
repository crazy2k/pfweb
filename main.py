#!/usr/bin/python

import web

import pages

urls = (
	'/',			'pages.login',
	'/login',		'pages.login',
	'/auth',		'pages.auth',
	'/logout',		'pages.logout',
	'/index',		'pages.index',
	'/setmateria',		'pages.setmateria',
	'/corregirnota',	'pages.corregirnota',
	'/personal',		'pages.personal',
	'/register',		'pages.register',
)

web.internalerror = web.debugerror

if __name__ == "__main__": web.run(urls)

