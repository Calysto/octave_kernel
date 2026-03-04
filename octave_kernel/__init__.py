"""An Octave kernel for Jupyter"""

from ._version import __version__
from .kernel import OctaveKernel

__all__ = ["OctaveKernel", "__version__"]
