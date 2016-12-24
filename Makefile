# Note: This is meant for octave_kernel developer use only
.PHONY: all clean test release

export NAME=octave_kernel
export VERSION=`python -c "import $(NAME); print($(NAME).__version__)"`

all: clean
	python setup.py install

clean:
	rm -rf build
	rm -rf dist

test: clean
	pip install jupyter_kernel_test nbconvert
	python setup.py build
	python -m octave_kernel.install
	python test_octave_kernel.py
	jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=octave --ExecutePreprocessor.timeout=60 --stdout octave_kernel.ipynb > /dev/null;
	make clean

release: clean
	pip install wheel
	python setup.py register
	rm -rf dist
	python setup.py bdist_wheel --universal
	python setup.py sdist
	git tag v$(VERSION)
	git push origin --all
	git push origin --tags
	twine upload dist/*
