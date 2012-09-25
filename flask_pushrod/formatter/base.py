from werkzeug.exceptions import BadRequest


def formatter(name=None, mime_type=None):
    """
    Flags a function as a Pushrod formatter.
    However, before you can use it it must still be registered to the app's Pushrod instance.
    """

    if not name:
        name = ()
    if isinstance(name, basestring):
        name = (name,)

    if not mime_type:
        mime_type = ()
    if isinstance(mime_type, basestring):
        mime_type = (mime_type,)

    def decorator(f):
        f._is_pushrod_formatter = True
        f.formatter_names = name
        f.formatter_mime_types = mime_type

        return f

    return decorator


class FormatterNotFound(BadRequest):
    def __init__(self):
        super(FormatterNotFound, self).__init__(self,
            u"The requested formatter does not exist")
