# Note: This is meant for octave_kernel developer use only

PORT := "8888"

# List available recipes
default:
    @just --list

install:
    uv tool run prek install
    uv sync --group test

docker-build:
    docker build --rm --force-rm -t calysto/octave-notebook:latest .

docker-run:
    docker run -it --rm -p {{PORT}}:8888 calysto/octave-notebook

test *args="":
    uv run --group test pytest {{args}}

test-kernel:
    uv sync --group test
    uv run python -m unittest -v test_octave_kernel.py
    uv run python -m octave_kernel.check
    uv run python test_octave_kernel.py

test-notebook:
    uv run --group test jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=octave --ExecutePreprocessor.timeout=60 --stdout octave_kernel.ipynb > /dev/null

cover *args="":
    uv run --group coverage pytest --cov=octave_kernel --cov-report=term-missing --cov-fail-under=90 {{args}}
    uv run --with coverage coverage html

typing:
    uv run --group typing mypy . --install-types --non-interactive

pre-commit *args="":
    uv tool run prek --all-files {{args}}
