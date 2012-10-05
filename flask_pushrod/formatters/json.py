from __future__ import absolute_import


from .base import formatter

import json


@formatter('json', 'application/json')
def json_formatter(unformatted, **kwargs):
    """
    Formats a response using :func:`json.dumps`.

    :Formatter MIME type triggers: - application/json
    :Formatter name triggers: - json
    """
    return unformatted.formatted(
        json.dumps(unformatted.response),
        'application/json')
