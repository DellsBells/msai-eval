def query(data, pattern):
    def _query(d, p):
        if not isinstance(p, list) or len(p) == 0:
            return []
        key = p[0]
        if key in d and (isinstance(d[key], dict) or isinstance(d[key], list)):
            result = [_query(v, p[1:]) for v in d[key] if _match(key, v)]
            return [i for j in result for i in j]
        else:
            return []

    def _match(k, v):
        if '*' in k and not isinstance(v, dict) and not isinstance(v, list):
            return True
        elif '*' in k and (isinstance(v, dict) or isinstance(v, list)):
            return False
        elif k == '*':
            return True
        else:
            return key == v

    return _query(data, pattern)