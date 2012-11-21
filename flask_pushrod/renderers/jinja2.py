from __future__ import absolute_import


from .base import renderer

import flask


@renderer('html', 'text/html', normalize=False)
def jinja2_renderer(unrendered, jinja_template=None, **kwargs):
    """
    Renders a response using :func:`flask.render_template`.

    :Renderer MIME type triggers: - text/html
    :Renderer name triggers: - html
    """

    if jinja_template:
        return unrendered.rendered(
            flask.render_template(jinja_template, **unrendered.response),
            'text/html')
    else:
        return NotImplemented
