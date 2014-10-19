# Note: This is meant for Octave Kernel developer use only
.PHONY: all clean release test

export NAME=octave_kernel
export VERSION=`python -c "import $(NAME); print($(NAME).__version__)"`
export KILL_OCTAVE="from oct2py import kill_octave; kill_octave()"


all:
	make clean
	python setup.py install

clean:
	rm -rf build
	rm -rf dist
	find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f
	python -c $(KILL_OCTAVE)


release:
	make clean
	pip install wheel
	python setup.py register
	python setup.py bdist_wheel upload
	python setup.py sdist --formats=gztar,zip upload
	git tag v$(VERSION)
	git push origin --all
	git push origin --tags

test:
	make clean
	python setup.py install
	cd ~; ipython qtconsole --kernel=octave
	make clean
