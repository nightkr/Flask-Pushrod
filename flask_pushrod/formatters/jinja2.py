from __future__ import absolute_import


from .base import formatter

import flask


@formatter('html', 'text/html')
def jinja2_formatter(unformatted, template=None, **kwargs):
    """
    Formats a response using :func:`flask.render_template`.

    :Formatter MIME type triggers: - text/html
    :Formatter name triggers: - html
    """

    if template:
        return unformatted.formatted(
            flask.render_template(**unformatted.response),
            'application/json')
