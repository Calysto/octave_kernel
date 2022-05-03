# Note: This is meant for octave_kernel developer use only
.PHONY: data-files build install clean test docker-build docker-run


data-files: clean
	mkdir -p jupyter-data/share/jupyter/kernels/octave
	cp octave_kernel/kernel.json jupyter-data/share/jupyter/kernels/octave
	cp -r octave_kernel/images jupyter-data/share/jupyter/kernels/octave/images

install: data-files
	pip install -e ".[test]"


clean:
	rm -rf jupyter-data
	rm -rf build
	rm -rf dist


build: data-files
	pip install build twine
	python -m build .
	twine check --strict dist/*

docker-build:
	docker build --rm --force-rm -t calysto/octave-notebook:latest .

docker-run:
	docker run -it --rm -p $(PORT):8888 calysto/octave-notebook

test: clean
	python test_octave_kernel.py
	python -m octave_kernel.check
	jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=octave --ExecutePreprocessor.timeout=60 --stdout octave_kernel.ipynb > /dev/null;
	make clean
