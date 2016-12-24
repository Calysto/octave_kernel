A Jupyter kernel for Octave

This requires `Jupyter Notebook <http://jupyter.readthedocs.org/en/latest/install.html>`_, and Octave_ installed with gnuplot support.

To install::

    pip install octave_kernel
    python -m octave_kernel.install

To use it, run one of:

.. code:: shell

    ipython notebook
    # In the notebook interface, select Octave from the 'New' menu
    ipython qtconsole --kernel octave
    ipython console --kernel octave

This is based on `MetaKernel <http://pypi.python.org/pypi/metakernel>`_,
which means it features a standard set of magics.

A sample notebook is available online_.

You can specify the path to your Octave executable by creating an `OCTAVE_EXECUTABLE` environmental variable.

.. _Octave: https://www.gnu.org/software/octave/download.html
.. _online: http://nbviewer.ipython.org/github/Calysto/octave_kernel/blob/master/octave_kernel.ipynb
