# Note: This is meant for developer use only
.PHONY: all clean test release 

export TEST_ARGS=--exe -v --with-doctest
export NAME=octave_kernel
export VERSION=`python -c "import $(NAME); print($(NAME).__version__)"`

all: clean
	flit install --symlink

clean:
	rm -rf build
	rm -rf dist
	find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f

test: clean
	python test_octave_kernel.py

release: clean
	pip install wheel
	flit wheel --upload
	git tag v$(VERSION)
	git push origin --all
	git push origin --tags
