def normalize_basestring(x, pushrod):
    return unicode(x)


def normalize_iterable(x, pushrod):
    return [pushrod.normalize(i) for i in x]
