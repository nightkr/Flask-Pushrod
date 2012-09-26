from flask import Flask, Response

from .resolver import Pushrod, pushrod_view
from .formatters.base import formatter, UnformattedResponse
from .formatters.json import json_formatter

from unittest import TestCase
import json


test_response = {
    "spam": "eggs",
    "yes": [
        "maybe",
        "no",
    ],
    "nonsense": (
        True,
        False,
        "FILE_NOT_FOUND",
        -5.4,
    ),
}


@formatter('repr')
def repr_formatter(unformatted):
    return unformatted.formatted(repr(unformatted.response), "text/plain")


class PushrodTestCase(TestCase):
    def setUp(self):
        app = Flask(__name__)
        pushrod = Pushrod(app)

        pushrod.register_formatter(repr_formatter)
        pushrod.default_formatter = repr_formatter

        self.app = app
        self.client = app.test_client()


class PushrodResolverTestCase(PushrodTestCase):
    def test_raw_dict_response_data(self):
        @self.app.route("/raw_dict")
        @pushrod_view()
        def test_view_raw_dict():
            return test_response

        test_view_raw_dict_response = self.client.get("/raw_dict")
        assert test_view_raw_dict_response.status_code == 200
        assert test_view_raw_dict_response.data == repr(test_response)

    def test_response_data(self):
        @self.app.route("/200_response")
        @pushrod_view()
        def test_view_200_view():
            return UnformattedResponse(test_response)

        @self.app.route("/404_response")
        @pushrod_view()
        def test_view_404_view():
            return UnformattedResponse(test_response, 404)

        test_view_200_response = self.client.get("/200_response")
        assert test_view_200_response.status_code == 200
        assert test_view_200_response.data == repr(test_response)

        test_view_404_response = self.client.get("/404_response")
        assert test_view_404_response.status_code == 404
        assert test_view_404_response.data == repr(test_response)

    def test_response_bypass(self):
        @self.app.route("/raw_string")
        @pushrod_view()
        def test_raw_string_view():
            return "test"

        @self.app.route("/regular_response")
        @pushrod_view()
        def test_regular_response_view():
            return Response("test")

        test_raw_string_response = self.client.get("/raw_string")
        assert test_raw_string_response.status_code == 200
        assert test_raw_string_response.data == "test"

        test_regular_response_response = self.client.get("/regular_response")
        assert test_regular_response_response.status_code == 200
        assert test_regular_response_response.data == "test"


class PushrodFormatterTestCase(PushrodTestCase):
    def test_json_formatter(self):
        regular = json.dumps(test_response)
        formatted = self.app.pushrod.format_response(
            test_response, json_formatter)

        assert regular == formatted.data

        json.loads(formatted.data)
