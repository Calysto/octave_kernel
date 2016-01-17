"""Example use of jupyter_kernel_test, with tests for IPython."""

import unittest
import jupyter_kernel_test as jkt


class OctaveKernelTests(jkt.KernelTests):
    kernel_name = "octave"

    language_name = "octave"

    code_hello_world = "disp('hello, world')"

    completion_samples = [
        {
            'text': 'one',
            'matches': {'ones', 'onenormest'},
        },
    ]

    code_page_something = "ones?"

if __name__ == '__main__':
    unittest.main()
