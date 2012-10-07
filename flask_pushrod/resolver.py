from flask import current_app, request as current_request
from werkzeug.wrappers import BaseResponse

from . import renderers as _renderers
from .renderers import RendererNotFound, UnrenderedResponse

from functools import wraps


class Pushrod(object):
    """
    The main resolver class for Pushrod.

    :param renderers: A tuple of renderers that are registered immediately (can also be strings, which are currently expanded to flask.ext.pushrod.renderers.%s_renderer)
    """

    #: The query string argument checked for an explicit renderer (to override header-based content type negotiation).
    format_arg_name = "format"

    def __init__(self, app=None, renderers=('json', 'jinja2',), default_renderer=None):
        self.mime_type_renderers = {}
        self.named_renderers = {}
        self.default_renderer = None

        for renderer in renderers:
            if isinstance(renderer, basestring):
                renderer = getattr(_renderers, '%s_renderer' % renderer)

            self.register_renderer(renderer)

        if isinstance(default_renderer, basestring):
            default_renderer = self.named_renderers[default_renderer]
        self.default_renderer = default_renderer

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Registers the Pushrod resolver with the Flask app (can also be done by passing the app to the constructor).
        """

        app.pushrod = self

    def register_renderer(self, renderer, default=False):
        """
        Registers a renderer with the Pushrod resolver (can also be done by passing the renderer to the constructor).
        """

        if not renderer._is_pushrod_renderer:
            raise TypeError(u'Got passed an invalid renderer')

        for name in renderer.renderer_names:
            self.named_renderers[name] = renderer

        for mime_type in renderer.renderer_mime_types:
            self.mime_type_renderers[mime_type] = renderer

    def get_renderers_for_request(self, request=None):
        """
        Inspects a Flask :class:`~flask.Request` for hints regarding what renderer to use.

        :param request: The request to be inspected (defaults to :obj:`flask.request`)
        :returns: List of matching renderers, in order of user preference
        """

        if request is None:
            request = current_request

        if self.format_arg_name in request.args:
            renderer_name = request.args[self.format_arg_name]

            if renderer_name in self.named_renderers:
                return [self.named_renderers[renderer_name]]
            else:
                return []

        matching_renderers = [self.mime_type_renderers[mime_type]
                               for mime_type in request.accept_mimetypes.itervalues()
                               if mime_type in self.mime_type_renderers]

        if self.default_renderer:
            matching_renderers.append(self.default_renderer)

        return matching_renderers

    def render_response(self, response, renderer=None, renderer_kwargs=None):
        """
        Renders an unrendered response (a bare value, a (response, status, headers)-:obj:`tuple`, or an :class:`~flask.ext.pushrod.renderers.UnrenderedResponse` object).

        :throws RendererNotFound: If a usable renderer could not be found (explicit renderer argument points to an invalid render, or no acceptable mime types can be used as targets and there is no default renderer)
        :param response: The response to render
        :param renderer: The renderer(s) to use (defaults to using :meth:`get_renderer_for_request`)
        :param renderer_kwargs: Any extra arguments to pass to the renderer

        .. note::
           For convenience, a bare string (:obj:`unicode`, :obj:`str`, or any other :obj:`basestring` derivative), or a derivative of :class:`werkzeug.wrappers.BaseResponse` (such as :class:`flask.Response`) is passed through unchanged.
        .. note::
           A renderer may mark itself as unable to render a specific response by returning :obj:`None`, in which case the next possible renderer is attempted.
        """

        if renderer:
            if hasattr(renderer, "__iter__"):
                renderers = renderer
            else:
                renderers = [renderer]
        else:
            renderers = self.get_renderers_for_request()

        if renderer_kwargs is None:
            renderer_kwargs = {}

        if isinstance(response, (basestring, BaseResponse)):
            return response

        if not isinstance(response, UnrenderedResponse):
            if isinstance(response, tuple):
                response_raw, status, headers = response
                response = UnrenderedResponse(response, status, headers)
            else:
                response = UnrenderedResponse(response)

        for renderer in renderers:
            rendered = renderer(response, **renderer_kwargs)

            if rendered is not None:
                return rendered

        raise RendererNotFound()


def pushrod_view(**renderer_kwargs):
    """
    Decorator that wraps view functions and renders their responses through :meth:`flask.ext.pushrod.Pushrod.render_response`.

    :param renderer_kwargs: Any extra arguments to pass to the renderer
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*view_args, **view_kwargs):
            response = f(*view_args, **view_kwargs)
            return current_app.pushrod.render_response(response, renderer_kwargs=renderer_kwargs)

        return wrapper

    return decorator
