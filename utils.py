import web

def filterstr(s):
	import string
	allowed = string.ascii_letters + string.digits
	new = [c for c in s if c in allowed]
	new = string.join(new, '')
	return new

