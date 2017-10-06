An Octave kernel for Jupyter
============================
Prerequisites: Install  `Jupyter Notebook <http://jupyter.readthedocs.org/en/latest/install.html>`_, and Octave_.  It is recommended that you also
install ``gnuplot`` support in Octave for inline plotting.

To install::

    pip install octave_kernel

Add ``--user`` to install in your private environment.

To use it, run one of:

.. code:: shell

    ipython notebook
    # In the notebook interface, select Octave from the 'New' menu
    ipython qtconsole --kernel octave
    ipython console --kernel octave

This is based on `MetaKernel <http://pypi.python.org/pypi/metakernel>`_,
which means it features a standard set of magics.

A sample notebook is available online_.

You can specify the path to your Octave executable by creating an ``OCTAVE_EXECUTABLE`` environment variable.

You can also specify the command line options to Octave by creating an
``OCTAVE_CLI_OPTIONS`` environment variable.  The will be appended to the
default opions of  ``--interactive --quiet --no-init-file``.  Note that the
init file is explicitly called after the kernel has set ``more off`` to prevent
a lockup when the pager is invoked in ``~/.octaverc``.

.. _Octave: https://www.gnu.org/software/octave/download.html
.. _online: http://nbviewer.ipython.org/github/Calysto/octave_kernel/blob/master/octave_kernel.ipynb
