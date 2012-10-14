def _call_if_callable(x, *args, **kwargs):
    return x(*args, **kwargs) if callable(x) else x


def normalize_basestring(x, pushrod):
    return unicode(x)


def normalize_iterable(x, pushrod):
    return [pushrod.normalize(i) for i in x]


def normalize_dict(x, pushrod):
    normalized = dict((pushrod.normalize(unicode(k)), pushrod.normalize(v)) for k, v in x.items())
    return dict((k, v) for k, v in normalized.items() if v is not NotImplemented)


def normalize_int(x, pushrod):
    return int(x)


def normalize_float(x, pushrod):
    return float(x)


def normalize_bool(x, pushrod):
    return bool(x)


def normalize_none(x, pushrod):
    return None


def normalize_object(x, pushrod):
    if hasattr(x, '__pushrod_normalize__'):
        return x.__pushrod_normalize__(pushrod)

    if hasattr(x, '__pushrod_fields__'):
        fields = _call_if_callable(x.__pushrod_fields__)
        return pushrod.normalize(dict((name, pushrod.normalize(getattr(x, name))) for name in fields))

    if hasattr(x, '__pushrod_field__'):
        field = _call_if_callable(x.__pushrod_field__)
        return pushrod.normalize(getattr(x, field))

    return NotImplemented
