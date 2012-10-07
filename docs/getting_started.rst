Getting Started
===============

.. highlight:: python

Pushrod adds an extra layer between the Template and the View layers (from the Model-Template-View/MTV pattern, more commonly known as Model-View-Controller/MVC outside of the Python world), the renderer.

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

With Pushrod you don't do the rendering yourself in the View. Instead, you return a context which is passed to a renderer which is inferred from the request. This means that the same code-base can power both the UI and the API with minimal boilerplate. By default Pushrod is set up with a :func:`Jinja2 <flask.ext.pushrod.renderers.jinja2_renderer>` renderer (for HTML) and a :func:`JSON <flask.ext.pushrod.renderers.json_renderer>` renderer.

The first step is to add a Pushrod resolver and decorate the view with the :func:`~flask.ext.pushrod.pushrod_view` decorator, which will pass it through the Pushrod rendering pipeline. The code will still work because strings and :class:`~flask.Response` objects are passed through unrendered. The code should now look like this::

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
   While bare strings and Response objects are passed through unchanged, the (response, status, headers)-tuples are not; they are instead used to construct :class:`~flask.ext.pushrod.renderers.UnrenderedResponse` objects.

.. warning::
   Remember to add the :func:`~flask.ext.pushrod.pushrod_view` decorator closer to the function definition than the :meth:`~flask.Flask.route` decorator.

While this works and all, we get absolutely no benefit from using Pushrod right now. So let's let Pushrod handle the rendering::

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

That's it. While it might seem a bit longer than the regular non-Pushrod code, you now get JSON rendering (and any other renderers you decide to enable) for free!

Making Your Own Renderer
------------------------

Sometimes the available Pushrod renderers might not meet your requirements. Fortunately, making your own renderer is very easy. Let's say you want a renderer that passes the response through :func:`~repr.repr`, it would look somewhat like this::

  from flask.ext.pushrod.renderers import renderer

  from repr import repr


  @renderer(name='repr', mime_type='text/plain')
  def repr_renderer(unrendered, **kwargs):
    return unrendered.rendered(
        repr(unrendered.response),
        'text/plain')

.. warning::
   Always take a ``**kwargs`` in your renderer, since other renderers might take arguments that don't matter to your renderer.

.. warning::
   Of course, you should never use :func:`~repr.repr` in production code, it is just an example to demostrate the syntax without having to go through the regular boilerplate code of creating the response ourselves..

And you would registere it to your :class:`~flask.ext.pushrod.Pushrod` instance using :meth:`~flask.ext.pushrod.Pushrod.register_renderer`.

.. note::
   Functions not decorated using :func:`~flask.ext.pushrod.renderers.renderer` may not be registered as renderers.
