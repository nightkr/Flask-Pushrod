Getting Started
===============

.. highlight:: python

Pushrod adds an extra layer between the Template and the View layers (from the Model-Template-View/MTV pattern, more commonly known as Model-View-Controller/MVC outside of the Python world), the renderer.

Hello, World!
-------------

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
^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes the available Pushrod renderers might not meet your requirements. Fortunately, making your own renderer is very easy. Let's say you want a renderer that passes the response through :func:`~repr.repr`, it would look like this::

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
   Of course, you should never use :func:`~repr.repr` like this in production code, it is just an example to demostrate the syntax without having to go through the regular boilerplate code of creating the response ourselves.

And you would register it to your :class:`~flask.ext.pushrod.Pushrod` instance using :meth:`~flask.ext.pushrod.Pushrod.register_renderer`.

.. note::
   Functions not decorated using :func:`~flask.ext.pushrod.renderers.renderer` may not be registered as renderers.

Formatting Actually Useful Data
-------------------------------

.. note::
   This guide assumes that you're familiar with `Flask`_ and `Flask-SQLAlchemy`_.

While the shown examples might look neat for simple data, it can quickly get out of hand. For example, let's take a simple blog application (:ref:`let's call it pushrodr just to be original <flask:tutorial-introduction>`):

.. literalinclude:: ../examples/pushrodr/step1.py

Enter Normalizers
^^^^^^^^^^^^^^^^^

As you can see that quickly starts looking redundant, and *stupid*. It's also going to cause problems if you're going to do any form validation using, say, `Flask-WTF`_, or anything else that, while working perfectly for an API too, has special helpers for the GUI rendering. To help with these cases Flask-Pushrod has something called "normalizers". Normalizers are callables that take two arguments (the object and the :class:`~flask.ext.pushrod.Pushrod` instance) and prepare the data for serialization (see :meth:`~flask.ext.pushrod.Pushrod.normalize`). If a normalizer returns :obj:`NotImplemented` then the value is passed through to the next normalizer.


.. warning::
   Renderers can opt out of the normalization process, so that they are passed the un-normalized data (an example is :func:`the Jinja2 renderer <flask.ext.pushrod.renderers.jinja2_renderer>`). Because of this, the normalizer shouldn't add or rename data.


An example normalizer could look like this::

  def my_normalizer(x, pushrod):
      if x:
          return NotImplemented
      else:
          return 0

This would return 0 for all "falsy" values, but let all "trueish" values normalize as usual. It could then be registered like this::

    app = Flask(__name__)
    pushrod = Pushrod(app)
    pushrod.normalizer_fallbacks[object] = my_normalizer

.. note::
   There is also :attr:`~flask.ext.pushrod.Pushrod.normalizer_overrides`. The difference is that :attr:`~flask.ext.pushrod.Pushrod.normalizer_fallbacks` is a :obj:`dict` of callables that should be used for the "standard" case, while :attr:`~flask.ext.pushrod.Pushrod.normalizer_overrides` is a :obj:`dict` of :obj:`lists <list>` of callables should be used when you need to override the behaviour for a subset of cases.

.. note::
   Both :attr:`~flask.ext.pushrod.Pushrod.normalizer_overrides` and :attr:`~flask.ext.pushrod.Pushrod.normalizer_fallbacks` are resolved in the regular "MRO" (method resolution order). Normalization is resolved in the same order as method calls.

.. note::
   :attr:`~flask.ext.pushrod.Pushrod.normalizer_overrides` is a :class:`~collections.defaultdict`, so there is no need to create the :obj:`list` yourself.

Throwing Normalizers At The Problem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that you should have a basic grasp on normalizers, let's try to use some! Below is how the previous code would look using normalizers:

.. literalinclude:: ../examples/pushrodr/step2.py

Moving The Normalizers Into The Classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the spirit of converters like :meth:`__bool__`, the normalizers can also be defined inline in the classes, like this:

.. literalinclude:: ../examples/pushrodr/step3.py

Simplifying The Normalizers Even Further
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While it's much better than the original, as you can see the normalizers are all of the kind ``{'y': x.y}``. However, the inline normalizer syntax, also has a shortcut for defining fields to include, like this:

.. literalinclude:: ../examples/pushrodr/step4.py

.. note::
   There is also another shortcut for inline definition, for delegation. It's used like this, and it simply uses that field instead of itself (in this case, ``x.that_field``::

     __pushrod_field__ = "that_field"

.. _flask: http://flask.pocoo.org/
.. _flask-sqlalchemy: http://packages.python.org/Flask-SQLAlchemy/
.. _flask-wtf: http://packages.python.org/Flask-WTF/