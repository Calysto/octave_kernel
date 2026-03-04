"""Tests for OctaveKernel public API."""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from metakernel import ProcessMetaKernel
from octave_kernel._version import __version__
from octave_kernel.kernel import HELP_LINKS, STDIN_PROMPT, OctaveKernel

_DEFAULT_PLOT_SETTINGS: dict[str, Any] = {
    "backend": "inline",
    "format": "png",
    "width": -1,
    "height": -1,
    "resolution": 0,
    "name": "Figure",
    "plot_dir": None,
}


@pytest.fixture
def kernel():
    """OctaveKernel with mocked dependencies, bypassing Jupyter infrastructure.

    Uses object.__new__ to skip Jupyter/traitlets __init__, then pre-populates
    the traitlets _trait_values dict so trait attribute access works normally.
    """
    k = object.__new__(OctaveKernel)
    # Minimal traitlets state so trait __get__/__set__ work correctly.
    k._trait_values = {
        "plot_settings": _DEFAULT_PLOT_SETTINGS.copy(),
        "cli_options": "",
        "inline_toolkit": "",
    }
    k._trait_notifiers = {}
    k._trait_validators = {}
    k._cross_validation_lock = False
    # Kernel state
    k._octave_engine = MagicMock()
    k._language_version = "9.1.0"
    k.log = logging.getLogger(__name__)
    k.Error = MagicMock()  # type: ignore[method-assign]
    k.Display = MagicMock()  # type: ignore[method-assign]
    return k


# ---------------------------------------------------------------------------
# language_version
# ---------------------------------------------------------------------------


class TestLanguageVersion:
    """Tests for OctaveKernel.language_version."""

    def test_returns_cached_value(self, kernel):
        kernel._language_version = "9.1.0"
        assert kernel.language_version == "9.1.0"
        kernel._octave_engine.eval.assert_not_called()

    def test_queries_octave_when_uncached(self, kernel):
        kernel._language_version = None
        kernel._octave_engine.eval.return_value = "ans = 9.1.0"
        result = kernel.language_version
        assert result == "9.1.0"
        kernel._octave_engine.eval.assert_called_once_with("version", silent=True)

    def test_parses_last_word_from_output(self, kernel):
        kernel._language_version = None
        kernel._octave_engine.eval.return_value = "ans = 8.4.0"
        assert kernel.language_version == "8.4.0"

    def test_caches_result_after_first_query(self, kernel):
        kernel._language_version = None
        kernel._octave_engine.eval.return_value = "9.1.0"
        _ = kernel.language_version
        _ = kernel.language_version
        kernel._octave_engine.eval.assert_called_once()


# ---------------------------------------------------------------------------
# language_info
# ---------------------------------------------------------------------------


class TestLanguageInfo:
    """Tests for OctaveKernel.language_info."""

    def test_returns_dict(self, kernel):
        assert isinstance(kernel.language_info, dict)

    def test_mimetype(self, kernel):
        assert kernel.language_info["mimetype"] == "text/x-octave"

    def test_name(self, kernel):
        assert kernel.language_info["name"] == "octave"

    def test_file_extension(self, kernel):
        assert kernel.language_info["file_extension"] == ".m"

    def test_version_matches_language_version(self, kernel):
        assert kernel.language_info["version"] == kernel.language_version

    def test_contains_help_links(self, kernel):
        assert kernel.language_info["help_links"] == HELP_LINKS


# ---------------------------------------------------------------------------
# banner
# ---------------------------------------------------------------------------


class TestBanner:
    """Tests for OctaveKernel.banner."""

    def test_is_string(self, kernel):
        assert isinstance(kernel.banner, str)

    def test_contains_octave_version(self, kernel):
        assert kernel.language_version in kernel.banner

    def test_contains_kernel_version(self, kernel):
        assert __version__ in kernel.banner


# ---------------------------------------------------------------------------
# octave_engine property
# ---------------------------------------------------------------------------


class TestOctaveEngineProperty:
    """Tests for OctaveKernel.octave_engine."""

    def test_returns_existing_engine(self, kernel):
        mock_engine = MagicMock()
        kernel._octave_engine = mock_engine
        assert kernel.octave_engine is mock_engine

    def test_creates_engine_when_none(self, kernel):
        kernel._octave_engine = None
        with patch("octave_kernel.kernel.OctaveEngine") as MockEngine:
            result = kernel.octave_engine
        MockEngine.assert_called_once()
        assert result is MockEngine.return_value

    def test_stores_created_engine(self, kernel):
        kernel._octave_engine = None
        with patch("octave_kernel.kernel.OctaveEngine") as MockEngine:
            kernel.octave_engine
        assert kernel._octave_engine is MockEngine.return_value

    def test_new_engine_uses_plot_settings(self, kernel):
        kernel._octave_engine = None
        with patch("octave_kernel.kernel.OctaveEngine") as MockEngine:
            kernel.octave_engine
        assert MockEngine.call_args.kwargs["plot_settings"] == _DEFAULT_PLOT_SETTINGS

    def test_new_engine_uses_defer_startup(self, kernel):
        kernel._octave_engine = None
        with patch("octave_kernel.kernel.OctaveEngine") as MockEngine:
            kernel.octave_engine
        assert MockEngine.call_args.kwargs["defer_startup"] is True

    def test_new_engine_uses_cli_options(self, kernel):
        kernel._octave_engine = None
        kernel._trait_values["cli_options"] = "--no-gui"
        with patch("octave_kernel.kernel.OctaveEngine") as MockEngine:
            kernel.octave_engine
        assert MockEngine.call_args.kwargs["cli_options"] == "--no-gui"


# ---------------------------------------------------------------------------
# makeWrapper
# ---------------------------------------------------------------------------


class TestMakeWrapper:
    """Tests for OctaveKernel.makeWrapper()."""

    def test_returns_engine_repl(self, kernel):
        repl = MagicMock()
        kernel._octave_engine.repl = repl
        assert kernel.makeWrapper() is repl


# ---------------------------------------------------------------------------
# do_execute_direct
# ---------------------------------------------------------------------------


class TestDoExecuteDirect:
    """Tests for OctaveKernel.do_execute_direct()."""

    def test_quit_clears_engine(self, kernel):
        kernel.do_shutdown = MagicMock()
        kernel.do_execute_direct("quit")
        assert kernel._octave_engine is None

    def test_quit_calls_do_shutdown(self, kernel):
        kernel.do_shutdown = MagicMock()
        kernel.do_execute_direct("quit")
        kernel.do_shutdown.assert_called_once_with(True)

    def test_quit_with_parens(self, kernel):
        kernel.do_shutdown = MagicMock()
        kernel.do_execute_direct("quit()")
        assert kernel._octave_engine is None

    def test_exit_clears_engine(self, kernel):
        kernel.do_shutdown = MagicMock()
        kernel.do_execute_direct("exit")
        assert kernel._octave_engine is None

    def test_exit_with_parens(self, kernel):
        kernel.do_shutdown = MagicMock()
        kernel.do_execute_direct("exit()")
        assert kernel._octave_engine is None

    def test_calls_startup_when_not_started(self, kernel):
        kernel._octave_engine._has_startup = False
        kernel._octave_engine.make_figures.return_value = None
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("1 + 1")
        kernel._octave_engine._startup.assert_called_once()

    def test_skips_startup_when_already_started(self, kernel):
        kernel._octave_engine._has_startup = True
        kernel._octave_engine.make_figures.return_value = None
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("1 + 1")
        kernel._octave_engine._startup.assert_not_called()

    def test_silent_skips_make_figures(self, kernel):
        kernel._octave_engine._has_startup = True
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("1 + 1", silent=True)
        kernel._octave_engine.make_figures.assert_not_called()

    def test_non_silent_calls_make_figures(self, kernel):
        kernel._octave_engine._has_startup = True
        kernel._octave_engine.make_figures.return_value = None
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("1 + 1", silent=False)
        kernel._octave_engine.make_figures.assert_called_once()

    def test_displays_all_returned_figures(self, kernel):
        kernel._octave_engine._has_startup = True
        images = [MagicMock(), MagicMock(), MagicMock()]
        kernel._octave_engine.make_figures.return_value = "/tmp/plots"
        kernel._octave_engine.extract_figures.return_value = images
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("plot(1)")
        assert kernel.Display.call_count == 3

    def test_extract_figures_called_with_plot_dir(self, kernel):
        kernel._octave_engine._has_startup = True
        kernel._octave_engine.make_figures.return_value = "/tmp/figs"
        kernel._octave_engine.extract_figures.return_value = []
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("plot(1)")
        kernel._octave_engine.extract_figures.assert_called_once_with("/tmp/figs", True)

    def test_no_display_when_no_plot_dir(self, kernel):
        kernel._octave_engine._has_startup = True
        kernel._octave_engine.make_figures.return_value = None
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("1 + 1")
        kernel.Display.assert_not_called()

    def test_make_figures_exception_calls_error_handler(self, kernel):
        kernel._octave_engine._has_startup = True
        kernel._octave_engine.make_figures.side_effect = Exception("plot error")
        with patch.object(ProcessMetaKernel, "do_execute_direct", return_value=None):
            kernel.do_execute_direct("plot(1)")
        kernel.Error.assert_called_once()


# ---------------------------------------------------------------------------
# get_kernel_help_on
# ---------------------------------------------------------------------------


class TestGetKernelHelpOn:
    """Tests for OctaveKernel.get_kernel_help_on()."""

    def test_empty_obj_returns_empty_string(self, kernel):
        assert kernel.get_kernel_help_on({"help_obj": ""}) == ""

    def test_missing_obj_returns_empty_string(self, kernel):
        assert kernel.get_kernel_help_on({}) == ""

    def test_multiword_obj_returns_empty_string(self, kernel):
        assert kernel.get_kernel_help_on({"help_obj": "foo bar"}) == ""

    def test_empty_obj_returns_none_on_fail(self, kernel):
        result = kernel.get_kernel_help_on({"help_obj": ""}, none_on_fail=True)
        assert result is None

    def test_multiword_obj_returns_none_on_fail(self, kernel):
        result = kernel.get_kernel_help_on({"help_obj": "a b"}, none_on_fail=True)
        assert result is None

    def test_valid_obj_returns_help_text(self, kernel):
        kernel._octave_engine.eval.return_value = "help text"
        result = kernel.get_kernel_help_on({"help_obj": "ones"})
        assert result == "help text"

    def test_valid_obj_calls_eval_with_help_command(self, kernel):
        kernel._octave_engine.eval.return_value = ""
        kernel.get_kernel_help_on({"help_obj": "zeros"})
        kernel._octave_engine.eval.assert_called_once_with("help zeros", silent=True)


# ---------------------------------------------------------------------------
# Print
# ---------------------------------------------------------------------------


class TestPrint:
    """Tests for OctaveKernel.Print().

    OctaveKernel.Print filters STDIN prompts before delegating to super().
    Tests use a plain-function patch on ProcessMetaKernel.Print so that the
    super() descriptor protocol binds self correctly and we can capture args.
    """

    def test_normal_arg_forwarded_to_super(self, kernel):
        received: list[Any] = []

        def capture(self, *args, **kwargs):
            received.extend(args)

        with patch.object(ProcessMetaKernel, "Print", capture):
            kernel.Print("hello")
        assert received == ["hello"]

    def test_multiple_normal_args_forwarded(self, kernel):
        received: list[Any] = []

        def capture(self, *args, **kwargs):
            received.extend(args)

        with patch.object(ProcessMetaKernel, "Print", capture):
            kernel.Print("foo", "bar")
        assert received == ["foo", "bar"]

    def test_standalone_stdin_prompt_suppresses_all_output(self, kernel):
        received: list[Any] = []

        def capture(self, *args, **kwargs):
            received.extend(args)

        with patch.object(ProcessMetaKernel, "Print", capture):
            kernel.Print(STDIN_PROMPT)
        assert received == []

    def test_stdin_prompt_with_whitespace_suppresses_output(self, kernel):
        received: list[Any] = []

        def capture(self, *args, **kwargs):
            received.extend(args)

        with patch.object(ProcessMetaKernel, "Print", capture):
            kernel.Print("  " + STDIN_PROMPT + "  ")
        assert received == []

    def test_prompt_prefix_is_stripped_from_arg(self, kernel):
        received: list[Any] = []

        def capture(self, *args, **kwargs):
            received.extend(args)

        with patch.object(ProcessMetaKernel, "Print", capture):
            kernel.Print(STDIN_PROMPT + "Enter value: ")
        assert received == ["Enter value: "]


# ---------------------------------------------------------------------------
# raw_input
# ---------------------------------------------------------------------------


class TestRawInput:
    """Tests for OctaveKernel.raw_input()."""

    def test_strips_stdin_prompt_before_forwarding(self, kernel):
        received: list[Any] = []

        def capture(self, text):
            received.append(text)
            return "user_input"

        with patch.object(ProcessMetaKernel, "raw_input", capture):
            kernel.raw_input(STDIN_PROMPT + "Enter: ")
        assert received == ["Enter: "]

    def test_clean_text_forwarded_unchanged(self, kernel):
        received: list[Any] = []

        def capture(self, text):
            received.append(text)
            return "user_input"

        with patch.object(ProcessMetaKernel, "raw_input", capture):
            kernel.raw_input("Enter name: ")
        assert received == ["Enter name: "]

    def test_returns_value_from_super(self, kernel):
        def capture(self, text):
            return "42"

        with patch.object(ProcessMetaKernel, "raw_input", capture):
            result = kernel.raw_input("Enter: ")
        assert result == "42"


# ---------------------------------------------------------------------------
# get_completions
# ---------------------------------------------------------------------------


class TestGetCompletions:
    """Tests for OctaveKernel.get_completions()."""

    def test_returns_list(self, kernel):
        kernel._octave_engine.eval.return_value = "foo\nbar"
        assert isinstance(kernel.get_completions({"obj": "f"}), list)

    def test_splits_output_into_completions(self, kernel):
        kernel._octave_engine.eval.return_value = "acos\nacosd\nacosh"
        assert kernel.get_completions({"obj": "acos"}) == ["acos", "acosd", "acosh"]

    def test_empty_output_returns_empty_list(self, kernel):
        kernel._octave_engine.eval.return_value = ""
        assert kernel.get_completions({"obj": "zzz_no_match"}) == []

    def test_calls_completion_matches(self, kernel):
        kernel._octave_engine.eval.return_value = ""
        kernel.get_completions({"obj": "sin"})
        kernel._octave_engine.eval.assert_called_once_with(
            'completion_matches("sin")', silent=True
        )


# ---------------------------------------------------------------------------
# handle_plot_settings
# ---------------------------------------------------------------------------


class TestHandlePlotSettings:
    """Tests for OctaveKernel.handle_plot_settings()."""

    def test_syncs_current_plot_settings_to_engine(self, kernel):
        kernel.handle_plot_settings()
        assert kernel._octave_engine.plot_settings == _DEFAULT_PLOT_SETTINGS

    def test_syncs_updated_plot_settings_to_engine(self, kernel):
        new_settings = {"backend": "svg", "format": "svg"}
        kernel._trait_values["plot_settings"] = new_settings
        kernel.handle_plot_settings()
        assert kernel._octave_engine.plot_settings == new_settings
