from __future__ import absolute_import


from .base import renderer

import json


@renderer('json', 'application/json', normalize=True)
def json_renderer(unrendered, **kwargs):
    """
    Renders a response using :func:`json.dumps`.

    :Renderer MIME type triggers: - application/json
    :Renderer name triggers: - json
    """
    return unrendered.rendered(
        json.dumps(unrendered.response),
        'application/json')
