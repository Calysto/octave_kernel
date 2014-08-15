A simple IPython kernel for Octave

This requires IPython 3, which is not yet released, and `oct2py <http://pypi.python.org/pypi/oct2py>`_.

To test it, install with ``setup.py``, then::

    ipython qtconsole --kernel octave

It supports command history, calltips, the ``?`` help magic,
and completion.  You can toggle inline plotting using ``%inline``.

For details of how this works, see IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_.
