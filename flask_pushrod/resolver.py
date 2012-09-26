from flask import current_app, request as current_request
from werkzeug.wrappers import BaseResponse

from . import formatters
from .formatters import FormatterNotFound, UnformattedResponse

from functools import wraps


class Pushrod(object):
    format_arg_name = "format"

    def __init__(self, app=None, formatters=[], default_formatter=None):
        self.mime_type_formatters = {}
        self.named_formatters = {}
        self.default_formatter = None

        for formatter in formatters:
            if isinstance(formatter, basestring):
                formatter = getattr(formatters, '%s_formatter' % formatter)

            self.register_formatter(formatter)

        if isinstance(default_formatter, basestring):
            default_formatter = self.named_formatters[default_formatter]
        self.default_formatter = default_formatter

        if app:
            self.init_app(app)

    def init_app(self, app):
        app.pushrod = self

    def register_formatter(self, formatter, default=False):
        if not formatter._is_pushrod_formatter:
            raise TypeError(u'Got passed an invalid formatter')

        for name in formatter.formatter_names:
            self.named_formatters[name] = formatter

        for mime_type in formatter.formatter_mime_types:
            self.mime_type_formatters[mime_type] = formatter

    def get_formatter_for_request(self, request=None):
        if request is None:
            request = current_request

        if self.format_arg_name in request.args:
            formatter_name = request.args[self.format_arg_name]

            if formatter_name not in self.named_formatters:
                raise FormatterNotFound()

            return self.named_formatters[formatter_name]

        for mime_type in request.accept_mimetypes.itervalues():
            if mime_type in self.mime_type_formatters:
                return self.mime_type_formatters[mime_type]

        if self.default_formatter:
            return self.default_formatter

        raise FormatterNotFound()

    def format_response(self, response, formatter=None, formatter_kwargs=None):
        if formatter is None:
            formatter = self.get_formatter_for_request()
        if formatter_kwargs is None:
            formatter_kwargs = {}

        if isinstance(response, (basestring, BaseResponse)):
            return response

        if not isinstance(response, UnformattedResponse):
            if isinstance(response, tuple):
                response_raw, status, headers = response
                response = UnformattedResponse(response, status, headers)
            else:
                response = UnformattedResponse(response)

        formatted = formatter(response, **formatter_kwargs)

        return formatted


def pushrod_view(**formatter_kwargs):
    """
    Decorator for views that should be passed through Pushrod.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*view_args, **view_kwargs):
            response = f(*view_args, **view_kwargs)
            return current_app.pushrod.format_response(response, formatter_kwargs=formatter_kwargs)

        return wrapper

    return decorator
