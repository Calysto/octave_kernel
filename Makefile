# Note: This is meant for Octave Kernel developer use only
.PHONY: all clean test

export KILL_OCTAVE="from oct2py import kill_octave; kill_octave()"

all:
	make clean
	python setup.py install

clean:
	rm -rf build
	rm -rf dist
	find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f
	python -c $(KILL_OCTAVE)

test:
	make clean
	python setup.py install
	cd ~; ipython qtconsole --kernel=octave
	make clean
