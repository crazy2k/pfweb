import web

# Function generously provided by Anand Chitipothu (thanks, Anand!)
# with some changes to suit my needs.
def unflatten(d, separator="--"):
    """Convert flattened data into nested form.
    
        >>> unflatten({"a": 1, "b--x": 2, "b--y": 3, "c--0": 4, "c--1": 5})
        {'a': 1, 'c': [4, 5], 'b': {'y': 3, 'x': 2}}
        >>> unflatten({"a--0--x": 1, "a--0--y": 2, "a--1--x": 3, "a--1--y": 4})
        {'a': [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]}
        
    """
        
    def setvalue(data, k, v):
        if separator in k:
            k, k2 = k.split(separator, 1)
            setvalue(data.setdefault(k, {}), k2, v)
        else:
            data[k] = v

    d2 = {}
    for k, v in d.items():
        setvalue(d2, k, v)
    return d2

def filterstr(s):
    import string
    allowed = string.ascii_letters + string.digits
    new = [c for c in s if c in allowed]
    new = string.join(new, '')
    return new

