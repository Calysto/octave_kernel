import sys
from metakernel import __version__ as mversion
from . import __version__
from .kernel import OctaveKernel


if __name__ == "__main__":
    print('Octave kernel v%s' % __version__)
    print('Metakernel v%s' % mversion)
    print('Python v%s' % sys.version)
    print('Python path: %s' % sys.executable)
    print('\nConnecting to Octave...')
    try:
        o = OctaveKernel()
        print('Octave connection established')
        print(o.banner)
        e = o.octave_engine
        toolkits = e.eval('available_graphics_toolkits', silent=True)[8:]
        print('Graphics toolkit: %s' % e._default_toolkit)
        print('Available toolkits: %s' % toolkits)
    except Exception as e:
        print(e)
