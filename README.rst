A Jupyter kernel for Octave

This requires `Jupyter Notebook <http://jupyter.readthedocs.org/en/latest/install.html>`_, and Octave installed with gnuplot support.

Install as ``pip install octave_kernel``.

Then, you can select the "Octave" Kernel in the Jupyter Notebook.

This is based on `MetaKernel <http://pypi.python.org/pypi/metakernel>`_,
which means it features a standard set of magics.

A sample notebook is available online_.

You can specify the path to your Octave executable by creating an `OCTAVE_EXECUTABLE` environmental variable.

.. _online: http://nbviewer.ipython.org/github/Calysto/octave_kernel/blob/master/octave_kernel.ipynb
