from functools import wraps


class Pushrod(object):
    mime_type_formatters = {}
    named_formatters = {}
    default_formatter = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.pushrod = self

    def format_response(self):
        pass


def view(**formatter_kwargs):
    """
    Decorator for views that should be passed through Pushrod.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*view_args, **view_kwargs):
            f(*view_args, **view_kwargs)

        return f

    return decorator
