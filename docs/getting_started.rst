Getting Started
===============

.. highlight:: python

Pushrod adds an extra layer between the Template and the View layers (from the Model-Template-View/MTV pattern, more commonly known as Model-View-Controller/MVC outside of the Python world), the formatter.

A Starting Point
----------------

As an example, we're going to adapt this simple Flask app (slightly adapted from the Flask hello world example) to Pushrod::

  from flask import Flask, render_template

  import random


  app = Flask(__name__)


  @app.route("/")
  def hello():
  	return render_template("hello.html", greeting=random.choice(("Hi", "Heya")))

  if __name__ == "__main__":
  	app.run()

Where :file:`hello.html` might look like this:

.. code-block:: html+jinja

   <html>
   	<head>
   	</head>
   	<body>
   	 Hello, {{ greeting }}.
   	</body>
   </html>

Adapting It To Pushrod
----------------------

With Pushrod you don't do the rendering yourself in the View. Instead, you return a context which is passed to a formatter which is inferred from the request. This means that the same code-base can power both the UI and the API with minimal boilerplate. By default Pushrod is set up with a :func:`Jinja2 <flask.ext.pushrod.formatters.jinja2_formatter>` formatter (for HTML) and a :func:`JSON <flask.ext.pushrod.formatters.json_formatter>` formatter.

The first step is to add a Pushrod resolver and decorate the view with the :func:`~flask.ext.pushrod.pushrod_view` decorator, which will pass it through the Pushrod formatting pipeline. The code will still work because strings and :class:`~flask.Response` objects are passed through unformatted. The code should now look like this::

  from flask import Flask, render_template
  from flask.ext.pushrod import Pushrod, pushrod_view

  import random


  app = Flask(__name__)
  Pushrod(app)


  @app.route("/")
  @pushrod_view()
  def hello():
  	return render_template("hello.html", greeting=random.choice(("Hi", "Heya")))

  if __name__ == "__main__":
  	app.run()

.. warning::
   While bare strings and Response objects are passed through unchanged, the (response, status, headers) tuples are not; they are instead used to construct :class:`~flask.ext.pushrod.formatters.UnformattedResponse` objects.

.. warning::
   Remember to add the :func:`~flask.ext.pushrod.pushrod_view` decorator closer to the function definition than :meth:`~flask.Flask.route` decorator.

While this works and all, we get absolutely no benefit from using Pushrod right now. So let's let Pushrod handle the formatting::

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

That's it. While it might seem a bit longer than the regular non-Pushrod code, you now get JSON formatting (and any other formatters you decide to enable) for free!

Making Your Own Formatter
-------------------------

Sometimes the available Pushrod formatters might not meet your requirements. Fortunately, making your own formatter is very easy. Let's say you want a formatter that passes the response through :func:`~repr.repr`, it would look somewhat like this::

  from flask.ext.pushrod.formatters import formatter

  from repr import repr


  @formatter(name='repr', mime_type='text/plain')
  def repr_formatter(unformatted, **kwargs):
    return unformatted.formatted(
        repr(unformatted.response),
        'text/plain')

.. warning::
   Always take a **kwargs in your formatter, since other formatters might take arguments that don't matter to your formatter.

.. warning::
   Of course, you should never use :func:`~repr.repr` in production code, it is just an example to demostrate the syntax without having to go through the regular boilerplate code of creating the response ourselves..

And you would registere it to your :class:`~flask.ext.pushrod.Pushrod` instance using :meth:`~flask.ext.pushrod.Pushrod.register_formatter`.

.. note::
   Functions not decorated using :func:`~flask.ext.pushrod.formatters.formatter` may not be registered as formatters.
