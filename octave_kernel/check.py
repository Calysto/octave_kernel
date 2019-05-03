import sys
from metakernel import __version__ as mversion
from . import __version__
from .kernel import OctaveEngine


if __name__ == "__main__":
    print('Octave kernel v%s' % __version__)
    print('Metakernel v%s' % mversion)
    print('Python v%s' % sys.version)
    print('Python path: %s' % sys.executable)
    print('\nConnecting to Octave...')
    try:
        o = OctaveEngine()
        o.eval('disp("Octave connection established!")')
        oversion = o.eval('version', silent=True).split()[-1]
        toolkits = o.eval('available_graphics_toolkits', silent=True)[8:]
        print('Octave v%s' % oversion)
        print('Graphics toolkit: %s' % o._default_toolkit)
        print('Available toolkits: %s' % toolkits)
    except Exception as e:
        print(e)
