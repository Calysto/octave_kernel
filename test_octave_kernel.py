"""Example use of jupyter_kernel_test, with tests for IPython."""

import unittest
import jupyter_kernel_test as jkt


class OctaveKernelTests(jkt.KernelTests):
    def setUp(self) -> None:
        # Make sure any initial output is emitted (for example toolkit warnings).
        self.execute_helper(self.code_hello_world)

    kernel_name = "octave"

    language_name = "octave"

    code_hello_world = "disp('hello, world')"

    # TODO
    # code_display_data = (
    #     [
    #         {"code": "%plot -f png\nplot([1,2,3])", "mime": "image/png"},
    #         {"code": "%plot -f svg\nplot([1,2,3])", "mime": "image/svg+xml"},
    #     ]
    #     if sys.platform == "linux"
    #     else []
    # )

    completion_samples = [
        {
            "text": "acos",
            "matches": {"acos", "acosd", "acosh"},
        },
    ]

    code_page_something = "ones?"

    code_inspect_sample = "ones"


if __name__ == "__main__":
    unittest.main()
