import sys
from . import __version__
from .kernel import OctaveEngine


if __name__ == "__main__":
    try:
        o = OctaveEngine()
        o.eval('disp("Octave connection established!")')
        raise RuntimeError('hi')
    except Exception as e:
        print(e)
        print('Octave kernel: %s' % __version__)
        print('Python: %s' % sys.version)
        print('Python path: %s' % sys.executable)
