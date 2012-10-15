"""
Flask-Pushrod ships with a few normalizers by default. For more info, see :meth:`~flask.ext.pushrod.Pushrod.normalize`.

Flask-Pushrod's built-in normalizers are generally named with the scheme :samp:`normalize_{type}`.

.. note::
   Normalizers also apply to subclasses, unless the subclass defines another normalizer.
"""


def _call_if_callable(x, *args, **kwargs):
    return x(*args, **kwargs) if callable(x) else x


def normalize_basestring(x, pushrod):
    """
    :takes:
      - :obj:`basestring`
      - :obj:`~datetime.datetime`
      - :obj:`~datetime.time`
      - :obj:`~datetime.date`
    :returns: :obj:`unicode`
    """
    return unicode(x)


def normalize_iterable(x, pushrod):
    """
    :takes:
      - :obj:`list`
      - :obj:`tuple`
      - generator (see :pep:`255`, :pep:`342`, and :pep:`289`)
    :returns: :obj:`list` with all values :meth:`normalized <flask.ext.pushrod.Pushrod.normalize>`
    """
    return [pushrod.normalize(i) for i in x]


def normalize_dict(x, pushrod):
    """
    :takes: :obj:`dict`
    :returns: :obj:`dict` with all keys converted to :obj:`unicode` and then :meth:`normalized <flask.ext.pushrod.Pushrod.normalize>` and all values :meth:`normalized <flask.ext.pushrod.Pushrod.normalize>`
    """
    normalized = dict((pushrod.normalize(unicode(k)), pushrod.normalize(v)) for k, v in x.items())
    return dict((k, v) for k, v in normalized.items() if v is not NotImplemented)


def normalize_int(x, pushrod):
    """
    :takes:
      - :obj:`int`
      - :obj:`long`
    :returns: :obj:`int` or :obj:`long`
    """
    return int(x)


def normalize_float(x, pushrod):
    """
    :takes: :obj:`float`
    :returns: :obj:`float`
    """
    return float(x)


def normalize_bool(x, pushrod):
    """
    :takes: :obj:`bool`
    :returns: :obj:`bool`
    """
    return bool(x)


def normalize_none(x, pushrod):
    """
    :takes: :obj:`None`
    :returns: :obj:`None`
    """
    return None


def normalize_object(x, pushrod):
    """
    Delegates normalization to the object itself, looking for the following attributes/methods (in this order):

    - __pushrod_normalize__ - Essentially treated as if a normalizer was explicitly registered
    - __pushrod_fields__ - A list of names fields, which is essentially treated like ``{k: getattr(x, k) for k in x.__pushrod_fields__}``
    - __pushrod_field__ - A name of a single field, x is then substituted for what is (simplified) ``getattr(x, x.__pushrod_field)``

    .. note::
       __pushrod_fields__ and __pushrod_field__ can be either a callable or an attribute, while __pushrod_normalize__ must be a callable.

    :takes: :obj:`object`
    """
    if hasattr(x, '__pushrod_normalize__'):
        return x.__pushrod_normalize__(pushrod)

    if hasattr(x, '__pushrod_fields__'):
        fields = _call_if_callable(x.__pushrod_fields__)
        return pushrod.normalize(dict((name, pushrod.normalize(getattr(x, name))) for name in fields))

    if hasattr(x, '__pushrod_field__'):
        field = _call_if_callable(x.__pushrod_field__)
        return pushrod.normalize(getattr(x, field))

    return NotImplemented
