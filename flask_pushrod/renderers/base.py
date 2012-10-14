from werkzeug.exceptions import NotAcceptable

from flask import current_app, Response

from functools import wraps


class UnrenderedResponse(object):
    """
    Holds basic response data from the view function until it is processed by the renderer.
    """

    #: The class to construct with the rendered response, defaults to :class:`flask.Response`.
    rendered_class = Response

    def __init__(self, response=None, status=None, headers=None):
        self.response = response
        self.status = status
        self.headers = headers

    def rendered(self, rendered_response, mime_type):
        """
        Constructs a :attr:`rendered_class` (:class:`flask.Response` by default) based on the response parameters.
        """

        return self.rendered_class(rendered_response,
            self.status, self.headers,
            mime_type)


def renderer(name=None, mime_type=None, normalize=True):
    """
    Flags a function as a Pushrod renderer.

    .. note::
       Before it is recognized by :meth:`flask.ext.pushrod.Pushrod.get_renderers_for_request` (and, by extension, :meth:`~flask.ext.pushrod.Pushrod.render_response`) it must be registered to the app's :class:`~flask.ext.pushrod.Pushrod` instance (using :meth:`~flask.ext.pushrod.Pushrod.register_renderer`, or passed as part of the ``renderers`` argument to the :class:`~flask.ext.pushrod.Pushrod` constructor).

    :param name: A :obj:`basestring` or a tuple of basestrings to match against when explicitly requested in the query string
    :param mime_type: A :obj:`basestring` or a tuple of basestrings to match against against when using HTTP content negotiation
    :param normalize: If True then the unrendered response will be passed through :meth:`flask.ext.pushrod.Pushrod.normalize`
    """

    if not name:  # pragma: no cover
        name = ()
    if isinstance(name, basestring):
        name = (name,)

    if not mime_type:  # pragma: no cover
        mime_type = ()
    if isinstance(mime_type, basestring):
        mime_type = (mime_type,)

    def decorator(f):
        f._is_pushrod_renderer = True
        f.renderer_names = name
        f.renderer_mime_types = mime_type

        @wraps(f)
        def wrapper(unrendered, **kwargs):
            if normalize:
                unrendered.response = current_app.extensions['pushrod'].normalize(unrendered.response)
            return f(unrendered, **kwargs)

        return wrapper

    return decorator


class RendererNotFound(NotAcceptable):
    """
    Thrown when no acceptable renderer can be found, see :meth:`flask.ext.pushrod.Pushrod.get_renderers_for_request`.

    .. note::
       This class inherits from :exc:`werkzeug.exceptions.NotAcceptable`, so it's automatically converted to ``406 Not Acceptable`` by Werkzeug if not explicitly handled (which is usually the intended behaviour).
    """

    def __init__(self):
        super(RendererNotFound, self).__init__(
            u"The requested renderer does not exist")
