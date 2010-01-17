import web

#  Function generously provided by Anand Chitipothu. (Thanks, Anand!)
def unflatten(d, seperator="--"):
	"""Convert flattened data into nested form.
	
		>>> unflatten({"a": 1, "b--x": 2, "b--y": 3, "c--0": 4, "c--1": 5})
		{'a': 1, 'c': [4, 5], 'b': {'y': 3, 'x': 2}}
		>>> unflatten({"a--0--x": 1, "a--0--y": 2, "a--1--x": 3, "a--1--y": 4})
		{'a': [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]}
		
	"""
	def isint(k):
		try:
			int(k)
			return True
		except ValueError:
			return False
		
	def setvalue(data, k, v):
		if '--' in k:
			k, k2 = k.split(seperator, 1)
			setvalue(data.setdefault(k, {}), k2, v)
		else:
			data[k] = v
			
	def makelist(d):
		"""Convert d into a list if all the keys of d are integers."""
		if isinstance(d, dict):
			if all(isint(k) for k in d.keys()):
				return [makelist(d[k]) for k in sorted(d.keys(), key=int)]
			else:
				return web.storage((k, makelist(v)) for k, v in d.items())
		else:
			return d
			
	d2 = {}
	for k, v in d.items():
		setvalue(d2, k, v)
	return makelist(d2)

def filterstr(s):
	import string
	allowed = string.ascii_letters + string.digits
	new = [c for c in s if c in allowed]
	new = string.join(new, '')
	return new

