An Octave kernel for Jupyter
============================

.. image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/Calysto/octave_kernel/main?urlpath=/lab/tree/octave_kernel.ipynb

Prerequisites
-------------
`Jupyter Notebook <http://jupyter.readthedocs.org/en/latest/install.html>`_ and GNU Octave_.

Installation
------------
To install using pip::

    pip install octave_kernel

Add ``--user`` to install in the user-level environment instead of the system environment.

To install using conda::

    conda config --add channels conda-forge
    conda install octave_kernel
    conda install texinfo # For the inline documentation (shift-tab) to appear.

We require the ``octave-cli`` or ``octave`` executable to run the kernel.
Add that executable's directory to the ``PATH`` environment variable or create the
environment variable ``OCTAVE_EXECUTABLE`` to point to the executable itself.
Note that on Octave 5+ on Windows, the executable is in ``"Octave-x.x.x.x\mingw64\bin"``.

We automatically install a Jupyter kernelspec when installing the
python package.  This location can be found using ``jupyter kernelspec list``.
If the default location is not desired, remove the directory for the
``octave`` kernel, and install using ``python -m octave_kernel install``.  See
``python -m octave_kernel install --help`` for available options.

Usage
-----
To use the kernel, run one of:

.. code:: shell

    jupyter notebook  # or ``jupyter lab``, if available
    # In the notebook interface, select Octave from the 'New' menu
    jupyter qtconsole --kernel octave
    jupyter console --kernel octave

This kernel is based on `MetaKernel <http://pypi.python.org/pypi/metakernel>`_,
which means it features a standard set of magics (such as ``%%html``).  For a full list of magics,
run ``%lsmagic`` in a cell.

A sample notebook is available online_.


Configuration
-------------
The kernel can be configured by adding an ``octave_kernel_config.py`` file to the
``jupyter`` config path.  The ``OctaveKernel`` class offers ``plot_settings``, ``inline_toolkit``,
``kernel_json``, and ``cli_options`` as configurable traits.  The available plot settings are:
'format', 'backend', 'width', 'height', 'resolution', and 'plot_dir'.

.. code:: bash

    cat ~/.jupyter/octave_kernel_config.py
    # use Qt as the default backend for plots
    c.OctaveKernel.plot_settings = dict(backend='qt')


The path to the Octave kernel JSON file can also be specified by creating an
``OCTAVE_KERNEL_JSON`` environment variable.

The command line options to Octave can also be specified with an
``OCTAVE_CLI_OPTIONS`` environment variable.  The cli options be appended to the
default options of  ``--interactive --quiet --no-init-file``.  Note that the
init file is explicitly called after the kernel has set ``more off`` to prevent
a lockup when the pager is invoked in ``~/.octaverc``.

The inline toolkit is the ``graphics_toolkit`` used to generate plots for the inline
backend.  It defaults to ``qt``.  The different backend can be used for inline
plotting either by using this configuration or by using the plot magic and putting the backend name after ``inline:``, e.g. ``plot -b inline:fltk``.


Troubleshooting
---------------

Kernel Times Out While Starting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If the kernel does not start, run the following command from a terminal:

.. code:: shell

    python -m octave_kernel.check

This can help diagnose problems with setting up integration with Octave.  If in doubt,
create an issue with the output of that command.


Kernel is Not Listed
~~~~~~~~~~~~~~~~~~~~
If the kernel is not listed as an available kernel, first try the following command:

.. code:: shell

    python -m octave_kernel install --user

If the kernel is still not listed, verify that the following point to the same
version of python:

.. code:: shell

    which python  # use "where" if using cmd.exe
    which jupyter


Gnuplot Error
~~~~~~~~~~~~~
An error that starts with ``gnuplot> set terminal aqua enhanced title`` can be fixed by
adding ``setenv("GNUTERM","qt");`` to ``~/.octaverc`` on MacOS or by installing
``gunplot-x11`` and using ``setenv("GNUTERM", "X11")``.

Octave-Snap (Linux)
~~~~~~~~~~~~~~~~~~~
You can check if you are using a snap version on Linux by checking the path to your Octave
installation.

.. code:: shell

    which octave

If the returned path has ``snap`` in it, then Octave is running in a container and you will need to configure the kernel appropriately.

1) Set the environment variable ``OCTAVE_EXECUTABLE="octave"``

.. code:: shell

    echo export OCTAVE_EXECUTABLE=\"octave\" >> ~/.bashrc

2) Make a directory for the temporary plot directories that the kernel uses. This *cannot* be a hidden directory.

.. code:: shell

    mkdir ~/octavePlots

3) Set ``plot_dir`` to point to your plot directory in ``octave_kernel_config.py``.

.. code:: shell

    c.OctaveKernel.plot_settings = dict(plot_dir='<home>/octavePlots')

where ``<home>`` is the absolute path to your home directory. Do not use ``~`` as this resolves to a different location for Octave-Snap.


Blank Plot
~~~~~~~~~~
Specify a different format using the ``%plot -f <backend>`` magic or using a configuration setting.
On some systems, the default ``'png'`` produces a black plot.  On other systems ``'svg'`` produces a
black plot.

Local Installation
------------------

To install from a git checkout run:

.. code:: shell

    pip install -e .


.. _Octave: https://octave.org/download
.. _online: http://nbviewer.ipython.org/github/Calysto/octave_kernel/blob/main/octave_kernel.ipynb
