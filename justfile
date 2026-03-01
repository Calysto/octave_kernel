# Note: This is meant for octave_kernel developer use only

PORT := "8888"

install:
    uv sync --extra test

docker-build:
    docker build --rm --force-rm -t calysto/octave-notebook:latest .

docker-run:
    docker run -it --rm -p {{PORT}}:8888 calysto/octave-notebook

test:
    uv run --extra test python test_octave_kernel.py
    uv run python -m octave_kernel.check
    uv run --extra test jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=octave --ExecutePreprocessor.timeout=60 --stdout octave_kernel.ipynb > /dev/null
