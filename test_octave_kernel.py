"""Example use of jupyter_kernel_test, with tests for IPython."""

import queue
import sys
import unittest
from typing import ClassVar

import jupyter_kernel_test as jkt
import pytest

from octave_kernel._utils import is_sandboxed_octave


class OctaveKernelTests(jkt.KernelTests):  # type:ignore[misc]
    kernel_name = "octave"

    @classmethod
    def setUpClass(cls) -> None:
        pass  # Kernel is started per-test in setUp instead.

    @classmethod
    def tearDownClass(cls) -> None:
        pass  # Kernel is stopped per-test in tearDown instead.

    def setUp(self) -> None:
        self.km, self.kc = jkt.start_new_kernel(kernel_name=self.kernel_name)
        # Make sure any initial output is emitted (for example toolkit warnings).
        self.execute_helper(self.code_hello_world)

    def tearDown(self) -> None:
        self.kc.stop_channels()
        self.km.shutdown_kernel()

    language_name = "octave"

    code_hello_world = "disp('hello, world')"

    code_display_data: ClassVar = (
        []
        if sys.platform == "win32" or is_sandboxed_octave()
        else [
            {"code": "%plot -f png\nplot([1,2,3])", "mime": "image/png"},
            {"code": "%plot -f svg\nplot([1,2,3])", "mime": "image/svg+xml"},
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

    @pytest.mark.skipif(sys.platform == "win32", reason="Test does not work on windows")
    def test_doc_does_not_hang(self) -> None:
        """Test that doc command completes without hanging (issue #184)."""
        try:
            replies, _ = self.execute_helper("doc disp", timeout=10)
        except queue.Empty:
            self.fail("'doc' command timed out — kernel hung (issue #184)")
        self.assertEqual(replies["content"]["status"], "ok")

    @pytest.mark.skipif(sys.platform == "win32", reason="Test does not work on windows")
    def test_open_does_not_hang(self) -> None:
        """Test that open command completes without hanging (issue #184)."""
        try:
            replies, _ = self.execute_helper("open disp", timeout=10)
        except queue.Empty:
            self.fail("'open' command timed out — kernel hung (issue #184)")
        self.assertEqual(replies["content"]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
