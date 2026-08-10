# Note: This is meant for octave_kernel developer use only

PORT := "8888"

# List available recipes
default:
    @just --list

install:
    poetry sync --only main,dev,test
    poetry run pre-commit install

docker-build:
    docker build --rm --force-rm -t calysto/octave-notebook:latest .

test-docker: docker-build
    docker run --rm calysto/octave-notebook:latest jupyter kernelspec list | grep octave
    docker run --rm calysto/octave-notebook:latest octave --version

docker-run:
    docker run -it --rm -p {{PORT}}:8888 calysto/octave-notebook

test *args="":
    poetry sync --only main,test
    poetry run pytest {{args}}

test-kernel:
    poetry sync --only main,test
    poetry run python -m octave_kernel install --sys-prefix
    poetry run python -m unittest -v test_octave_kernel.py
    poetry run python -m octave_kernel.check
    poetry run python test_octave_kernel.py

test-notebook:
    poetry sync --only main,test
    poetry run jupyter execute --kernel_name octave octave_kernel.ipynb

cover *args="":
    poetry sync --only main,coverage
    poetry run pytest --cov=octave_kernel --cov-report=term-missing --cov-report=xml --cov-fail-under=90 {{args}}
    poetry run coverage html

typing:
    poetry sync --only main,typing
    poetry run mypy . --install-types --non-interactive

run-notebook:
    poetry sync --only main,test
    poetry run jupyter notebook octave_kernel.ipynb

test-manual:
    poetry sync --only main,dev
    poetry run python -m octave_kernel install --sys-prefix
    poetry run jupyter-console --kernel=octave

lint *args="":
    poetry sync --only main,dev
    poetry run pre-commit run --all-files {{args}}

lint-all *args="":
    poetry sync --only main,dev
    poetry run pre-commit run --all-files --hook-stage manual {{args}}

_asv-setup:
    poetry sync --only main,benchmark
    poetry run asv machine --yes

benchmark *args="": _asv-setup
    poetry run asv run HEAD^! {{args}}

benchmark-compare: _asv-setup
    poetry run asv continuous $(git merge-base HEAD origin/main) HEAD --split

docs:
    poetry sync --only main,docs
    poetry run mkdocs build

docs-serve:
    poetry sync --only main,docs
    poetry run mkdocs serve
