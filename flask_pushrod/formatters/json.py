from __future__ import absolute_import


from .base import formatter

import json


@formatter('json', 'application/json')
def json_formatter(unformatted):
    return unformatted.formatted(
        json.dumps(unformatted.response),
        'application/json')
