# An Octave kernel for Jupyter

[![image](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Calysto/octave_kernel/main?urlpath=/lab/tree/octave_kernel.ipynb)

## Prerequisites

[Jupyter Notebook](http://jupyter.readthedocs.org/en/latest/install.html) and GNU [Octave](https://octave.org/download).

## Installation

To install using pip:

```shell
pip install octave_kernel
```

To install using conda:

```shell
conda config --add channels conda-forge
conda install octave_kernel
conda install texinfo # For the inline documentation (shift-tab) to appear.
```

We require the `octave-cli` or `octave` executable to run the kernel. Add that executable's directory to the `PATH` environment variable or create the environment variable `OCTAVE_EXECUTABLE` to point to the executable itself. Note that on Octave 5+ on Windows, the executable is in `"Octave-x.x.x.x\mingw64\bin"`.

We automatically install a Jupyter kernelspec when installing the python package. This location can be found using `jupyter kernelspec list`. If the default location is not desired, remove the directory for the `octave` kernel, and install using `python -m octave_kernel install`. See `python -m octave_kernel install --help` for available options.

## Usage

To use the kernel, run one of:

```shell
jupyter notebook  # or ``jupyter lab``, if available
# In the notebook interface, select Octave from the 'New' menu
jupyter qtconsole --kernel octave
jupyter console --kernel octave
```

This kernel is based on [MetaKernel](http://pypi.python.org/pypi/metakernel), which means it features a standard set of magics (such as `%%html`). For a full list of magics, run `%lsmagic` in a cell.

A sample notebook is available [online](http://nbviewer.ipython.org/github/Calysto/octave_kernel/blob/main/octave_kernel.ipynb).

## Configuration

The kernel can be configured by adding an `octave_kernel_config.py` file to the `jupyter` config path. The `OctaveKernel` class offers `plot_settings`, `inline_toolkit`, `kernel_json`, and `cli_options` as configurable traits. The available plot settings are: 'format', 'backend', 'width', 'height', 'resolution', and 'plot_dir'.

```bash
cat ~/.jupyter/octave_kernel_config.py
# use Qt as the default backend for plots
c.OctaveKernel.plot_settings = dict(backend='qt')
```

The path to the Octave kernel JSON file can also be specified by creating an `OCTAVE_KERNEL_JSON` environment variable.

The command line options to Octave can also be specified with an `OCTAVE_CLI_OPTIONS` environment variable. The cli options be appended to the default options of `--interactive --quiet --no-init-file`. Note that the init file is explicitly called after the kernel has set `more off` to prevent a lockup when the pager is invoked in `~/.octaverc`.

The inline toolkit is the `graphics_toolkit` used to generate plots for the inline backend. It will default to whatever backend `octave` defaults to. The different backend can be used for inline plotting either by using this configuration or by using the plot magic and putting the backend name after `inline:`, e.g. `plot -b inline:fltk`.

## Supported Platforms

The `octave_kernel` supports running on Linux, MacOS, or Windows. On Linux, it supports Octave installed using `apt-get`, `flatpak`, or `snap`. There is no additional configuration required to use `flatpak` or `snap`.

## Managing the Octave Executable

The kernel resolves the Octave executable in this order:

1. The `executable` trait set in `octave_kernel_config.py`
1. The `OCTAVE_EXECUTABLE` environment variable
1. `octave` on `PATH`
1. `octave-cli` on `PATH`
1. `flatpak run org.octave.Octave` (if Flatpak is installed)

If none of the above resolves to a valid Octave installation, the kernel will fail to start with an error.

**Using a custom executable path**

Set the `OCTAVE_EXECUTABLE` environment variable before launching Jupyter:

```shell
export OCTAVE_EXECUTABLE=/opt/octave-9.3/bin/octave
jupyter lab
```

Or configure it persistently in `~/.jupyter/octave_kernel_config.py`:

```python
c.OctaveKernel.executable = "/opt/octave-9.3/bin/octave"
```

**Windows**

On Windows with Octave 5+, the executable lives under `Octave-x.x.x.x\mingw64\bin\`. Either add that directory to `PATH` or point `OCTAVE_EXECUTABLE` directly at `octave.exe`:

```bat
set OCTAVE_EXECUTABLE=C:\Octave\Octave-9.3.0\mingw64\bin\octave.exe
```

**Flatpak and Snap**

Flatpak and Snap installations are detected automatically - no additional configuration is needed. When a Snap installation is detected, the kernel uses a Snap-writable temp directory (`~/snap/octave/current/octave_kernel`) for figures.

**Validating the executable**

The kernel validates the configured executable at startup by running `octave --eval 'disp(version)'`. If validation fails, the kernel reports which executable was tried and exits with a clear error message. To diagnose the issue manually:

```shell
python -m octave_kernel.check
```

## Troubleshooting

### Debugging the Kernel

To see detailed Jupyter protocol messages and kernel log output, launch an interactive console session with debug logging:

```shell
pip install jupyter-console
jupyter console --log-level=debug --kernel=octave
```

`jupyter-console` is not installed by default and must be installed separately. This is useful for diagnosing communication issues between Jupyter and the kernel.

### Kernel Times Out While Starting

If the kernel does not start, run the following command from a terminal:

```shell
python -m octave_kernel.check
```

This can help diagnose problems with setting up integration with Octave. If in doubt, create an issue with the output of that command.

### Kernel is Not Listed

If the kernel is not listed as an available kernel, first try the following command:

```shell
python -m octave_kernel install --user
```

If the kernel is still not listed, verify that the following point to the same version of python:

```shell
which python  # use "where" if using cmd.exe
which jupyter
```

### Qt Backend Availability

In some cases, the `qt` graphics toolkit is only available when running with a display enabled.

On a remote system without a display, you can use `xvfb-run` to provide a virtual framebuffer. For example:

```shell
export OCTAVE_EXECUTABLE="xvfb-run octave"
```

Or in the config file:

```python
c.OctaveKernel.executable = "xvfb-run octave"
```

### JupyterHub with Qt Support

To enable Octave's Qt graphics toolkit in a JupyterHub environment (or any headless server), you need a virtual display. Install the required system packages:

```shell
apt-get install -y octave libglu1 xvfb texinfo fonts-freefont-otf ghostscript
```

Start `Xvfb` before launching JupyterHub (or in a server startup script):

```shell
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

Then configure the kernel to use the Qt backend:

```python
# ~/.jupyter/octave_kernel_config.py
c.OctaveKernel.plot_settings = dict(backend="qt")
```

For [Binder](https://mybinder.org)-based deployments, place a `start` script in the `binder/` directory to launch `Xvfb` and export `DISPLAY` before the server starts, and list the required packages in `binder/apt.txt`.

### Blank Plot

Specify a different format using the `%plot -f <backend>` magic or using a configuration setting. On some systems, the default `'png'` produces a black plot. On other systems `'svg'` produces a black plot.

## Local Installation

To install from a git checkout run:

```shell
pip install -e .
```
