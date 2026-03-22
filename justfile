# Note: This is meant for octave_kernel developer use only

PORT := "8888"

# List available recipes
default:
    @just --list

install:
    poetry install --with dev,test
    poetry run pre-commit install

docker-build:
    docker build --rm --force-rm -t calysto/octave-notebook:latest .

test-docker: docker-build
    docker run --rm calysto/octave-notebook:latest jupyter kernelspec list | grep octave
    docker run --rm calysto/octave-notebook:latest octave --version

docker-run:
    docker run -it --rm -p {{PORT}}:8888 calysto/octave-notebook

test *args="":
    poetry install --with test
    poetry run pytest {{args}}

test-kernel:
    poetry install --with test
    poetry run python -m octave_kernel install --sys-prefix
    poetry run python -m unittest -v test_octave_kernel.py
    poetry run python -m octave_kernel.check
    poetry run python test_octave_kernel.py

test-notebook:
    poetry install --with test
    poetry run jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=octave --ExecutePreprocessor.timeout=60 --stdout octave_kernel.ipynb > /dev/null

cover *args="":
    poetry install --with coverage
    poetry run pytest --cov=octave_kernel --cov-report=term-missing --cov-report=xml --cov-fail-under=90 {{args}}
    poetry run coverage html

typing:
    poetry install --with typing
    poetry run mypy . --install-types --non-interactive

run-notebook:
    poetry install --with test
    poetry run jupyter notebook octave_kernel.ipynb

lint:
    poetry install --with dev
    poetry run pre-commit run ruff-format --all-files
    poetry run pre-commit run ruff-check --all-files
    poetry run pre-commit run validate-pyproject --all-files
    poetry run pre-commit run poetry-check --all-files

pre-commit *args="":
    poetry install --with dev
    poetry run pre-commit run --all-files {{args}}

_asv-setup:
    poetry install --with benchmark
    poetry run asv machine --yes

benchmark *args="": _asv-setup
    poetry run asv run HEAD^! {{args}}

benchmark-compare: _asv-setup
    poetry run asv continuous $(git merge-base HEAD origin/main) HEAD --split

docs:
    poetry install --with docs
    poetry run mkdocs build

docs-serve:
    poetry install --with docs
    poetry run mkdocs serve
