"""Self check file"""

import sys

from metakernel import __version__ as mversion

from . import __version__
from .kernel import OctaveKernel

if __name__ == "__main__":
    print(f"Octave kernel v{__version__}")
    print(f"Metakernel v{mversion}")
    print(f"Python v{sys.version}")
    print(f"Python path: {sys.executable}")
    print("\nConnecting to Octave...")
    try:
        o = OctaveKernel()
        print("Octave connection established")
        print(o.banner)
        e = o.octave_engine
        e._startup()
        toolkits = e.eval("available_graphics_toolkits", silent=True)[8:]
        print(f"Graphics toolkit: {e._default_toolkit}")
        print(f"Available toolkits: {toolkits}")
    except Exception as e:
        print(e)
