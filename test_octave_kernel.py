"""Example use of jupyter_kernel_test, with tests for IPython."""

import unittest
from typing import ClassVar

import jupyter_kernel_test as jkt


class OctaveKernelTests(jkt.KernelTests):  # type:ignore[misc]
    def setUp(self) -> None:
        # Make sure any initial output is emitted (for example toolkit warnings).
        self.execute_helper(self.code_hello_world)

    kernel_name = "octave"

    language_name = "octave"

    code_hello_world = "disp('hello, world')"

    code_display_data: ClassVar = [
        {"code": "%plot -f png\nplot([1,2,3])", "mime": "image/png"},
        {"code": "%plot -f svg\nplot([1,2,3])", "mime": "image/svg+xml"},
    ]

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
