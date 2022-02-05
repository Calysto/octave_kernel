# Note: This is meant for octave_kernel developer use only
.PHONY: all clean test release docker-build docker-run

export NAME=`python setup.py --name 2>/dev/null`
export VERSION=`python setup.py --version 2>/dev/null`

all: clean
	pip install -e ".[test]"

clean:
	rm -rf build
	rm -rf dist

docker-build:
	docker build --rm --force-rm -t calysto/octave-notebook:latest .

docker-run:
	docker run -it --rm -p $(PORT):8888 calysto/octave-notebook

test: clean
	python test_octave_kernel.py
	python -m octave_kernel.check
	jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=octave --ExecutePreprocessor.timeout=60 --stdout octave_kernel.ipynb > /dev/null;
	make clean

release: test clean
	pip install wheel
	python setup.py register
	python setup.py bdist_wheel --universal
	python setup.py sdist
	git commit -a -m "Release $(VERSION)"; true
	git tag v$(VERSION)
	git push origin --all
	git push origin --tags
	twine upload dist/*
	printf '\nUpgrade octave_kernel-feedstock with release and sha256 sum:'
	shasum -a 256 dist/*.tar.gz
