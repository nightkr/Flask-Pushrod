API
===

.. automodule:: flask.ext.pushrod


Resolvers
---------

.. autoclass:: Pushrod
   :members:

Views
-----

.. autofunction:: pushrod_view

Renderers
----------

.. automodule:: flask.ext.pushrod.renderers

.. autofunction:: renderer

.. autoclass:: flask.ext.pushrod.renderers.UnrenderedResponse
   :members:

Bundled Renderers
^^^^^^^^^^^^^^^^^

.. autofunction:: json_renderer
.. autofunction:: jinja2_renderer

.. _bundled-normalizers:

Bundled Normalizers
-------------------

.. automodule:: flask.ext.pushrod.normalizers
   :members:
   :undoc-members:

.. autofunction:: normalize_basestring
.. autofunction:: normalize_iterable
.. autofunction:: normalize_dict
.. autofunction:: normalize_int
.. autofunction:: normalize_float
.. autofunction:: normalize_bool
.. autofunction:: normalize_none
.. autofunction:: normalize_object

Exceptions
----------

.. autoexception:: flask.ext.pushrod.renderers.RendererNotFound
