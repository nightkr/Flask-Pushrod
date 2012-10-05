from __future__ import absolute_import


from .base import formatter

import flask


@formatter('html', 'text/html')
def jinja2_formatter(unformatted, jinja_template=None, **kwargs):
    """
    Formats a response using :func:`flask.render_template`.

    :Formatter MIME type triggers: - text/html
    :Formatter name triggers: - html
    """

    if jinja_template:
        return unformatted.formatted(
            flask.render_template(jinja_template, **unformatted.response),
            'application/json')
