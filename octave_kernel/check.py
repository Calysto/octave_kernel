"""Self check file"""

import platform
import sys

import jupyter_client
from metakernel import __version__ as mversion

from . import __version__
from .kernel import OctaveKernel

if __name__ == "__main__":
    print(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python v{sys.version}")
    print(f"Python path: {sys.executable}")
    print(f"Octave kernel v{__version__}")
    print(f"Metakernel v{mversion}")
    print(f"Jupyter client v{jupyter_client.__version__}")
    print("\nConnecting to Octave...")
    try:
        o = OctaveKernel()
        print("Octave connection established")
        print(f"Banner: {o.banner}")
        e = o.octave_engine
        toolkits = e.eval("disp(available_graphics_toolkits)", silent=True).strip()
        toolkit = e.eval("disp(graphics_toolkit)", silent=True).strip()
        print(f"Graphics toolkit: {toolkit}")
        print(f"Available toolkits: {toolkits}")
    except Exception as e:
        print(e)
