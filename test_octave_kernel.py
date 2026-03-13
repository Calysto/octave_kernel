"""Example use of jupyter_kernel_test, with tests for IPython."""

import os
import subprocess
import sys
import unittest
from typing import ClassVar

import jupyter_kernel_test as jkt


def _is_sandboxed_octave() -> bool:
    """Return True if Octave is running via flatpak or snap."""
    exe = os.environ.get("OCTAVE_EXECUTABLE", "")
    if not exe:
        try:
            result = subprocess.run(["which", "octave"], capture_output=True, text=True)
            exe = result.stdout.strip()
        except Exception:
            pass
    return "flatpak" in exe or "snap" in exe


class OctaveKernelTests(jkt.KernelTests):  # type:ignore[misc]
    def setUp(self) -> None:
        # Make sure any initial output is emitted (for example toolkit warnings).
        self.execute_helper(self.code_hello_world)

    kernel_name = "octave"

    language_name = "octave"

    code_hello_world = "disp('hello, world')"

    code_display_data: ClassVar = (
        []
        if sys.platform == "win32" or _is_sandboxed_octave()
        else [
            {
                "code": "%plot -f png -b inline:gnuplot\nplot([1,2,3])",
                "mime": "image/png",
            },
            {
                "code": "%plot -f svg -b inline:gnuplot\nplot([1,2,3])",
                "mime": "image/svg+xml",
            },
        ]
    )

    complete_code_samples: ClassVar = [
        "disp('hello')",
        "x = 1 + 1",
        "exit",
    ]

    incomplete_code_samples: ClassVar = [
        "if true",
        "for i = 1:10",
        "while true",
        "function y = f(x)",
    ]

    completion_samples: ClassVar = [
        {
            "text": "acos",
            "matches": {"acos", "acosd", "acosh"},
        },
    ]

    code_page_something = "ones?"

    code_inspect_sample = "ones"


if __name__ == "__main__":
    unittest.main()
