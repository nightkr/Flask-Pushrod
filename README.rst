Flask-Pushrod
=============

.. image:: https://secure.travis-ci.org/dontcare4free/Flask-Pushrod.png
   :alt: Build Status
   :target: http://travis-ci.org/dontcare4free/Flask-Pushrod

Flask-Pushrod is a simple helper for Flask for doing content negotiation (primarily for running the API and the website on the same code-base, with as little separate handling as possible).

Installation
------------

Since Flask-Pushrod is still very early in development there is currently no official release available.

Usage
-----

A simple hello world app in Pushrod would look like this::

	from flask import Flask, render_template
	from flask.ext.pushrod import Pushrod, pushrod_view

	import random


	app = Flask(__name__)
	Pushrod(app)


	@app.route("/")
	@pushrod_view(jinja_template="hello.html")
	def hello():
	    return {
	        'greeting': random.choice(("Hi", "Heya"))
	    }

	if __name__ == "__main__":
	    app.run()

This would, depending on the request, return either the greeting message in JSON or render it through the Jinja2 `hello.html` template.

Tests
-----

::

$ python setup.py test


Documentation
-------------

More advanced documentation `is available on Read The Docs <http://flask-pushrod.rtfd.org/>`_.