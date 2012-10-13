def normalize_basestring(x, pushrod):
    return unicode(x)


def normalize_iterable(x, pushrod):
    return [pushrod.normalize(i) for i in x]


def normalize_dict(x, pushrod):
    return dict((pushrod.normalize(unicode(k)), pushrod.normalize(v)) for k, v in x.items())


def normalize_int(x, pushrod):
    return int(x)


def normalize_float(x, pushrod):
    return float(x)


def normalize_bool(x, pushrod):
    return bool(x)


def normalize_none(x, pushrod):
    return None
