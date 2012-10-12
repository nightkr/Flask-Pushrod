from flask import current_app, request as current_request
from werkzeug.wrappers import BaseResponse

from . import renderers as _renderers, normalizers
from .renderers import RendererNotFound, UnrenderedResponse

from functools import wraps
from collections import defaultdict

import logging


class Pushrod(object):
    """
    The main resolver class for Pushrod.

    :param renderers: A tuple of renderers that are registered immediately (can also be strings, which are currently expanded to flask.ext.pushrod.renderers.%s_renderer)
    """

    #: The query string argument checked for an explicit renderer (to override header-based content type negotiation).
    #:
    #: .. note::
    #:    This is set on the class level, not the instance level.
    format_arg_name = "format"

    @property
    def logger(self):
        """
        Gets the logger to use, mainly for internal use.

        The current resolution order looks as follows:

        - :attr:`self.app <app>`
        - :data:`flask.current_app`
        - :mod:`logging`
        """

        if self.app:
            return self.app.logger
        elif current_app:
            return current_app.logger
        else:
            return logging

    def __init__(self, app=None, renderers=('json', 'jinja2',), default_renderer='html'):
        #: The renderers keyed by MIME type.
        self.mime_type_renderers = {}
        #: The renderers keyed by output format name (such as html).
        self.named_renderers = {}

        #: Hooks for overriding a class' normalizer, even if they explicitly define one.
        #:
        #: All items should be lists of callables. All values default to an empty list.
        self.normalizer_overrides = defaultdict(lambda: [])
        #: Hooks for providing a class with a fallback normalizer, which is called only if it doesn't define one. All items should be callables.
        self.normalizer_fallbacks = {
            basestring: normalizers.normalize_basestring,
            list: normalizers.normalize_iterable,
        }

        #: The current app, only set from the constructor, not if using :meth:`init_app`.
        self.app = app or None

        for renderer in renderers:
            if isinstance(renderer, basestring):
                renderer = getattr(_renderers, '%s_renderer' % renderer)

            self.register_renderer(renderer)

        if isinstance(default_renderer, basestring):
            if default_renderer in self.named_renderers:
                default_renderer = self.named_renderers[default_renderer]
            else:
                self.logger.warning(u"Attempted to set the unrenderable format '%s' as the default format, disabling", default_renderer)
                default_renderer = None
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

        if not (hasattr(renderer, '_is_pushrod_renderer') and renderer._is_pushrod_renderer):
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
                response, status, headers = response
                response = UnrenderedResponse(response, status, headers)
            else:
                response = UnrenderedResponse(response)

        for renderer in renderers:
            rendered = renderer(response, **renderer_kwargs)

            if rendered is not None:
                return rendered

        raise RendererNotFound()

    def normalize(self, obj):
        """
        Runs an object through the normalizer mechanism, with the goal of producing a value consisting only of "native types" (:obj:`unicode`, :obj:`int`, :obj:`long`, :obj:`float`, :obj:`dict`, :obj:`list`, etc).

        The resolution order looks like this:

        - Loop through :attr:`self.normalizer_overrides[type(obj)] <normalizer_overrides>` (taking parent classes into account), should be a callable taking (obj, pushrod), falls through on :obj:`NotImplemented`
        - obj.__pushrod_normalize__, should be a callable taking the :class:`Pushrod` instance as an argument argument
        - obj.__pushrod_fields__, a :obj:`dict` is built where the key name is the field name and the value is ran normalized
        - obj.__pushrod_field__, a value which is normalized instead of obj
        - :attr:`self.normalizer_fallbacks[type(obj)] <normalizer_fallbacks` (taking parent classes into account), should be a callable taking (obj, pushrod), falls through on :obj:`NotImplemented`

        These are the default fallbacks:

        +-----------------+-----------------------------------------------------------+
        |Type             |Behaviour                                                  |
        +=================+===========================================================+
        |:obj:`basestring`|Converted to :obj:`unicode`                                |
        +-----------------+-----------------------------------------------------------+
        |:obj:`list`      |Values are normalized                                      |
        +-----------------+-----------------------------------------------------------+
        |:obj:`tuple`     |Converted to :obj:`list`, then normalized again            |
        +-----------------+-----------------------------------------------------------+
        |:obj:`dict`      |Keys are converted to :obj:`unicode`, values are normalized|
        +-----------------+-----------------------------------------------------------+
        |:obj:`int`       |Passed through                                             |
        +-----------------+-----------------------------------------------------------+
        |:obj:`long`      |Passed through                                             |
        +-----------------+-----------------------------------------------------------+
        |:obj:`float`     |Passed through                                             |
        +-----------------+-----------------------------------------------------------+

        :param obj: The object to normalize.
        """

        for cls in type(obj).__mro__:
            for override in self.normalizer_overrides[cls]:
                attempt = self.normalizer_overrides[cls](obj, self)
                if attempt is not NotImplemented:
                    return attempt

        if hasattr(obj, '__pushrod_normalize__'):
            return obj.__pushrod_normalize__(self)

        if hasattr(obj, '__pushrod_fields__'):
            return self.normalize(dict((name, self.normalize(getattr(obj, name))) for name in obj.__pushrod_fields__))

        if hasattr(obj, '__pushrod_field__'):
            return self.normalize(getattr(obj, obj.__pushrod_field__))

        for cls in type(obj).__mro__:
            if cls in self.normalizer_fallbacks:
                attempt = self.normalizer_fallbacks[cls](obj, self)
                if attempt is not NotImplemented:
                    return attempt

        return NotImplemented


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
