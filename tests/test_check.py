"""Tests for octave_kernel.check module.

All logic in check.py lives inside ``if __name__ == "__main__":`` so tests
execute it via ``runpy.run_module(..., run_name="__main__")``.  OctaveKernel
is patched at its definition site (``octave_kernel.kernel``) so the
``from .kernel import OctaveKernel`` inside the fresh runpy namespace picks up
the mock automatically.
"""

from __future__ import annotations

import io
import runpy
import sys
from unittest.mock import MagicMock, patch

import pytest
from metakernel import __version__ as mversion

from octave_kernel import __version__

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_check(mock_kernel_cls=None) -> str:
    """Execute check.py as __main__ and return captured stdout."""
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        if mock_kernel_cls is not None:
            with patch("octave_kernel.kernel.OctaveKernel", mock_kernel_cls):
                runpy.run_module("octave_kernel.check", run_name="__main__")
        else:
            runpy.run_module("octave_kernel.check", run_name="__main__")
    return buf.getvalue()


def _make_success_kernel(
    banner: str = "Octave Kernel v1.0 running GNU Octave v9.1.0",
    toolkit: str = "gnuplot",
    eval_result: str = "ans = {gnuplot}",
):
    """Return a mock OctaveKernel class whose instance simulates success."""
    inst = MagicMock()
    inst.banner = banner
    inst.octave_engine._default_toolkit = toolkit
    inst.octave_engine.eval.return_value = eval_result
    return MagicMock(return_value=inst), inst


# ---------------------------------------------------------------------------
# Module-scoped fixtures so each output string is produced only once.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def success_out() -> str:
    mock_cls, _ = _make_success_kernel()
    return _run_check(mock_cls)


@pytest.fixture(scope="module")
def failure_out() -> str:
    mock_cls = MagicMock(side_effect=Exception("could not start octave"))
    return _run_check(mock_cls)


# ---------------------------------------------------------------------------
# Static output — printed before the try block, always present
# ---------------------------------------------------------------------------


class TestStaticOutput:
    """Lines printed unconditionally regardless of Octave availability."""

    def test_prints_octave_kernel_version(self, success_out):
        assert __version__ in success_out

    def test_prints_metakernel_version(self, success_out):
        assert mversion in success_out

    def test_prints_python_version(self, success_out):
        ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert ver in success_out

    def test_prints_python_executable_path(self, success_out):
        assert sys.executable in success_out

    def test_prints_connecting_message(self, success_out):
        assert "Connecting to Octave" in success_out

    # Verify same static lines appear in the failure output too.

    def test_static_lines_present_on_failure(self, failure_out):
        assert __version__ in failure_out
        assert mversion in failure_out
        assert "Connecting to Octave" in failure_out


# ---------------------------------------------------------------------------
# Success-path output
# ---------------------------------------------------------------------------


class TestSuccessOutput:
    """Lines printed only when OctaveKernel starts successfully."""

    def test_prints_connection_established(self, success_out):
        assert "connection established" in success_out.lower()

    def test_prints_banner(self, success_out):
        assert "Octave Kernel v1.0 running GNU Octave v9.1.0" in success_out

    def test_prints_graphics_toolkit_label(self, success_out):
        assert "Graphics toolkit:" in success_out

    def test_prints_toolkit_name(self, success_out):
        assert "gnuplot" in success_out

    def test_prints_available_toolkits_label(self, success_out):
        assert "Available toolkits:" in success_out

    def test_calls_startup_on_engine(self):
        mock_cls, inst = _make_success_kernel()
        _run_check(mock_cls)
        inst.octave_engine._startup.assert_called_once()

    def test_calls_eval_for_available_toolkits(self):
        mock_cls, inst = _make_success_kernel()
        _run_check(mock_cls)
        inst.octave_engine.eval.assert_called_once_with(
            "available_graphics_toolkits", silent=True
        )

    def test_eval_result_sliced_into_toolkits(self):
        # eval returns "ans = {gnuplot}"; [8:] strips the first 8 chars.
        mock_cls, _inst = _make_success_kernel(eval_result="12345678rest")
        out = _run_check(mock_cls)
        assert "rest" in out

    def test_custom_banner_appears_in_output(self):
        mock_cls, _ = _make_success_kernel(banner="Custom Banner String")
        out = _run_check(mock_cls)
        assert "Custom Banner String" in out


# ---------------------------------------------------------------------------
# Failure-path output
# ---------------------------------------------------------------------------


class TestFailureOutput:
    """Behaviour when OctaveKernel() raises an exception."""

    def test_prints_exception_message(self, failure_out):
        assert "could not start octave" in failure_out

    def test_does_not_raise_to_caller(self):
        mock_cls = MagicMock(side_effect=RuntimeError("fatal error"))
        out = _run_check(mock_cls)  # must not propagate
        assert "fatal error" in out

    def test_exception_type_message_is_printed(self):
        mock_cls = MagicMock(side_effect=ValueError("bad value"))
        out = _run_check(mock_cls)
        assert "bad value" in out

    def test_no_connection_established_on_failure(self, failure_out):
        assert "connection established" not in failure_out.lower()

    def test_no_toolkit_info_on_failure(self, failure_out):
        assert "Graphics toolkit:" not in failure_out
        assert "Available toolkits:" not in failure_out
