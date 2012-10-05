from werkzeug.exceptions import NotAcceptable

from flask import Response


class UnformattedResponse(object):
    formatted_class = Response

    def __init__(self, response=None, status=None, headers=None):
        self.response = response
        self.status = status
        self.headers = headers

    def formatted(self, formatted_response, mime_type):
        return self.formatted_class(formatted_response,
            self.status, self.headers,
            mime_type)


def formatter(name=None, mime_type=None):
    """
    Flags a function as a Pushrod formatter.

    .. note::
       Before it is recognized by :meth:`flask.ext.pushrod.Pushrod.get_formatters_for_request` (and, by extension, :meth:`~flask.ext.pushrod.Pushrod.format_response`) it must be registered to the app's :class:`~flask.ext.pushrod.Pushrod` instance (using :meth:`~flask.ext.pushrod.Pushrod.register_formatter`, or passed as part of the ``formatters`` argument to the :class:`~flask.ext.pushrod.Pushrod` constructor).
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


class FormatterNotFound(NotAcceptable):
    """
    Thrown when no acceptable formatter can be found, see :meth:`flask.ext.pushrod.Pushrod.get_formatters_for_request`.

    .. note::
       This class inherits from :exc:`werkzeug.exceptions.NotAcceptable`, so it's automatically converted to ``406 Not Acceptable`` by Werkzeug if not explicitly handled (which is usually the intended behaviour).
    """

    def __init__(self):
        super(FormatterNotFound, self).__init__(
            u"The requested formatter does not exist")
