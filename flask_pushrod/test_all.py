from flask import Flask, Response, Request
import flask

from werkzeug.test import EnvironBuilder

from nose.tools import raises

from .resolver import Pushrod, pushrod_view
from .renderers.base import renderer, UnrenderedResponse, RendererNotFound
from .renderers.json import json_renderer
from .renderers.jinja2 import jinja2_renderer

from unittest import TestCase
import json

import logging


test_response_str = """
{
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
"""

test_response = eval(test_response_str)


@renderer('repr', normalize=False)
def repr_renderer(unrendered, **kwargs):
    return unrendered.rendered(repr(unrendered.response), "text/plain")


def test_logging_no_app():
    pushrod = Pushrod()
    assert pushrod.logger == logging


class PushrodTestCase(TestCase):
    def setUp(self):
        app = Flask(__name__,
            template_folder='test_templates',
        )
        app.testing = True
        pushrod = Pushrod(app)

        pushrod.register_renderer(repr_renderer)
        pushrod.default_renderer = repr_renderer

        self.app = app
        self.pushrod = app.extensions['pushrod']
        self.client = app.test_client()

        app_context = app.app_context()
        app_context.push()
        if not hasattr(self, 'app_contexts'):
            self.app_contexts = []
        self.app_contexts.append(app_context)

    def tearDown(self):
        self.app_contexts.pop().pop()

    def setup_method(self, method):
        # Setup for py.test
        return self.setUp()

    def teardown_method(self, method):
        # Setup for py.test
        return self.tearDown()


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
            return UnrenderedResponse(test_response)

        @self.app.route("/404_response")
        @pushrod_view()
        def test_view_404_view():
            return UnrenderedResponse(test_response, 404)

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

    @raises(RendererNotFound)
    def test_renderer_not_found(self):
        @self.app.route("/")
        @pushrod_view()
        def test_renderer_not_found_view():
            return {}

        response = self.client.get("/?format=none")
        assert response.status_code == 406, \
            "Status code returned from an unexistant renderer should be 406 (not acceptable)"

        with self.app.test_request_context("/?format=none"):
            self.pushrod.render_response(test_renderer_not_found_view(), "none")

    def test_constructor_renderer_registration(self):
        get_request_obj = lambda *args, **kwargs: Request(EnvironBuilder(*args, **kwargs).get_environ())

        pushrod = Pushrod(renderers=['json'])

        assert pushrod.default_renderer == None

        assert 'html' not in pushrod.named_renderers
        assert 'text/html' not in pushrod.mime_type_renderers

        assert 'json' in pushrod.named_renderers
        assert 'application/json' in pushrod.mime_type_renderers

        assert pushrod.named_renderers['json'] == json_renderer
        assert pushrod.mime_type_renderers['application/json'] == json_renderer

        assert pushrod.get_renderers_for_request(get_request_obj("/")) == []
        assert pushrod.get_renderers_for_request(get_request_obj("/?format=json")) == [json_renderer]

        pushrod = Pushrod(renderers=[repr_renderer])

        assert 'html' not in pushrod.named_renderers
        assert 'text/html' not in pushrod.named_renderers

        assert 'json' not in pushrod.named_renderers
        assert 'application/json' not in pushrod.mime_type_renderers

        assert 'repr' in pushrod.named_renderers

        assert pushrod.named_renderers['repr'] == repr_renderer

        assert pushrod.get_renderers_for_request(get_request_obj("/")) == []
        assert pushrod.get_renderers_for_request(get_request_obj("/?format=repr")) == [repr_renderer]

        pushrod = Pushrod(renderers=[repr_renderer], default_renderer='repr')

        assert pushrod.get_renderers_for_request(get_request_obj("/")) == [repr_renderer]

        with self.app.app_context():
            Pushrod(renderers=[])

        Pushrod(self.app, renderers=[])

        Pushrod(self.app, default_renderer=repr_renderer)

    @raises(TypeError)
    def test_register_invalid_renderer(self):
        def dummy():  # pragma: no cover
            pass

        self.pushrod.register_renderer(dummy)

    def test_render_tuple_response(self):
        response = self.pushrod.render_response((
            {u'aaa': u"hi"},  # Response value
            978,            # Status code
            {               # Headers
                'X-Aaa': "Hi!",
            },
        ), json_renderer)

        assert response.status_code == 978
        assert 'X-Aaa' in response.headers
        assert response.headers['X-Aaa'] == "Hi!"

        response_json = json.loads(response.data)

        assert u'aaa' in response_json
        assert response_json[u'aaa'] == u"hi"


class PushrodNormalizerTestCase(PushrodTestCase):
    def test_basestring_normalizer(self):
        from_unicode = self.pushrod.normalize(u"testing string")
        from_str = self.pushrod.normalize("testing string")

        assert from_unicode == u"testing string"
        assert from_str == u"testing string"

    def test_number_normalizer(self):
        assert self.pushrod.normalize(10) == 10
        assert self.pushrod.normalize(500L) == 500L
        assert self.pushrod.normalize(20.5) == 20.5

    def test_bool_normalizer(self):
        assert self.pushrod.normalize(True) == True

    def test_none_normalizer(self):
        assert self.pushrod.normalize(None) == None

    def test_iterable_normalizer(self):
        in_list = ["test string", 57]

        from_list = self.pushrod.normalize(in_list)
        from_tuple = self.pushrod.normalize(tuple(in_list))

        assert from_list == in_list
        assert from_tuple == in_list

    def test_dict_normalizer(self):
        in_dict = {
            "hi": 54,
            "bleh": "testable",
            "no": ["12"],
        }

        assert self.pushrod.normalize(in_dict) == in_dict

    def test_delegate_normalizer(self):
        class MyClass(object):
            __pushrod_field__ = "value"

            def __init__(self):
                self.value = 53.21

        my_instance = MyClass()

        assert self.pushrod.normalize(my_instance) == self.pushrod.normalize(my_instance.value)

    def test_no_normalizer(self):
        class MyClass(object):
            pass

        assert self.pushrod.normalize(MyClass()) == NotImplemented

        self.pushrod.normalizers[MyClass] = lambda x, pushrod: NotImplemented

        assert self.pushrod.normalize(MyClass()) == NotImplemented

    def test_dict_value_no_normalizer(self):
        class MyClass(object):
            pass

        assert self.pushrod.normalize({u"one": u"two", u"three": MyClass(), u"five": 6}) == {u"one": u"two", u"five": 6}

    def test_normalizer_method(self):
        class MyClass(object):
            def __pushrod_normalize__(self, pushrod):
                return u"Normalized!"

        assert self.pushrod.normalize(MyClass()) == u"Normalized!"

    def test_normalizer_generated_dict(self):
        class MyClass(object):
            __pushrod_fields__ = ["one", "three"]

            def __init__(self, one, two, three):
                self.one = one
                self.two = two
                self.three = three

        assert self.pushrod.normalize(MyClass('first', 'second', 'third')) == {u'one': u'first', u'three': u'third'}

    def test_normalizer_override(self):
        self.pushrod.normalizer_overrides[int].append(lambda x, pushrod: unicode(x) if x > 0 else NotImplemented)

        assert self.pushrod.normalize(0) == 0
        assert self.pushrod.normalize(1) == u"1"


class PushrodRendererTestCase(PushrodTestCase):
    def test_json_renderer(self):
        regular = json.dumps(test_response)
        rendered = self.pushrod.render_response(
            test_response, json_renderer)

        assert regular == rendered.data

        json.loads(rendered.data)

    @raises(RendererNotFound)
    def test_jinja_renderer_no_template(self):
        self.pushrod.render_response(
            test_response, jinja2_renderer)

    def test_jinja_renderer_no_template_fallback(self):
        self.pushrod.render_response(
            test_response, [jinja2_renderer, json_renderer])

    def test_jinja_renderer(self):
        regular = test_response_str

        with self.app.test_request_context():
            flask.current_app
            rendered = self.pushrod.render_response(
                test_response, jinja2_renderer, {'jinja_template': 'jinja.txt'})

        assert regular == rendered.data, \
            "'%s' does not equal '%s'" % (rendered.data, regular)

        assert eval(rendered.data) == test_response
