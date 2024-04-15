"""A custom hatch build hook for octave_kernel."""
import shutil
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomHook(BuildHookInterface):
    """The octave_kernel build hook."""

    def initialize(self, version, build_data):
        """Initialize the hook."""
        here = Path(__file__).parent.resolve()
        jupyter_data = here /"jupyter-data"
        if jupyter_data.exists():
            shutil.rmtree(jupyter_data)
        jupyter_data.mkdir()
        shutil.copy(here / "octave_kernel" / "kernel.json", jupyter_data / "kernel.json")
        shutil.copytree(here / "octave_kernel" / "images",  jupyter_data / "images")