"""Tests for OctaveEngine public and private API."""

from __future__ import annotations

import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from IPython.display import SVG
from metakernel import REPLWrapper

from octave_kernel.kernel import STDIN_PROMPT_REGEX, OctaveEngine


@pytest.fixture(scope="module")
def engine():
    """Shared OctaveEngine instance for the module."""
    eng = OctaveEngine()
    yield eng
    eng._cleanup()


# ---------------------------------------------------------------------------
# eval
# ---------------------------------------------------------------------------


class TestEval:
    """Tests for OctaveEngine.eval()."""

    def test_returns_string(self, engine):
        result = engine.eval("1 + 1", silent=True)
        assert isinstance(result, str)

    def test_basic_arithmetic(self, engine):
        result = engine.eval("1 + 1", silent=True)
        assert "2" in result

    def test_string_output(self, engine):
        result = engine.eval("disp('hello')", silent=True)
        assert "hello" in result

    def test_multiline_code(self, engine):
        result = engine.eval("x = 1;\ny = 2;\ndisp(x + y)", silent=True)
        assert "3" in result

    def test_silent_suppresses_stream_handler(self, engine):
        handler = MagicMock()
        old = engine.stream_handler
        engine.stream_handler = handler
        try:
            engine.eval("disp('test')", silent=True)
            handler.assert_not_called()
        finally:
            engine.stream_handler = old

    def test_non_silent_calls_stream_handler(self, engine):
        handler = MagicMock()
        old = engine.stream_handler
        engine.stream_handler = handler
        try:
            engine.eval("disp('hello')", silent=False)
            handler.assert_called()
        finally:
            engine.stream_handler = old

    def test_error_handler_called_on_repl_exception(self):
        error_handler = MagicMock()
        mock_repl = MagicMock()
        with patch.object(OctaveEngine, "_create_repl", return_value=mock_repl):
            eng = OctaveEngine(error_handler=error_handler, defer_startup=True)
        mock_repl.run_command.side_effect = Exception("repl error")
        result = eng.eval("bad")
        error_handler.assert_called_once()
        assert result == ""

    def test_no_error_handler_raises_on_repl_exception(self):
        mock_repl = MagicMock()
        with patch.object(OctaveEngine, "_create_repl", return_value=mock_repl):
            eng = OctaveEngine(defer_startup=True)
        mock_repl.run_command.side_effect = Exception("repl error")
        with pytest.raises(Exception, match="repl error"):
            eng.eval("bad")


# ---------------------------------------------------------------------------
# plot_settings
# ---------------------------------------------------------------------------


class TestPlotSettings:
    """Tests for the plot_settings property getter and setter."""

    def test_default_format(self, engine):
        assert engine.plot_settings["format"] == "png"

    def test_default_backend(self, engine):
        assert engine.plot_settings["backend"] == "inline"

    def test_default_width(self, engine):
        assert engine.plot_settings["width"] == -1

    def test_default_height(self, engine):
        assert engine.plot_settings["height"] == -1

    def test_default_resolution(self, engine):
        assert engine.plot_settings["resolution"] == 0

    def test_default_name(self, engine):
        assert engine.plot_settings["name"] == "Figure"

    def test_default_plot_dir(self, engine):
        assert engine.plot_settings["plot_dir"] is None

    def test_set_custom_format(self, engine):
        engine.plot_settings = {"backend": "inline", "format": "svg"}
        assert engine.plot_settings["format"] == "svg"
        engine.plot_settings = {"backend": "inline", "format": "png"}

    def test_none_values_replaced_with_defaults(self, engine):
        engine.plot_settings = {"width": None, "height": None}
        assert engine.plot_settings["width"] == -1
        assert engine.plot_settings["height"] == -1

    def test_none_settings_applies_defaults(self, engine):
        engine.plot_settings = None
        assert engine.plot_settings["backend"] == "inline"
        assert engine.plot_settings["format"] == "png"

    def test_inline_colon_backend(self, engine):
        engine.plot_settings = {"backend": "inline:gnuplot"}
        assert engine.plot_settings["backend"] == "inline:gnuplot"
        engine.plot_settings = {"backend": "inline"}

    def test_partial_settings_filled_with_defaults(self, engine):
        engine.plot_settings = {"format": "svg"}
        assert engine.plot_settings["backend"] == "inline"
        assert engine.plot_settings["width"] == -1
        engine.plot_settings = {"backend": "inline", "format": "png"}


# ---------------------------------------------------------------------------
# make_figures
# ---------------------------------------------------------------------------


class TestMakeFigures:
    """Tests for OctaveEngine.make_figures()."""

    def test_returns_directory_string_for_inline(self, engine):
        engine.plot_settings = {"backend": "inline"}
        plot_dir = engine.make_figures()
        assert isinstance(plot_dir, str)
        shutil.rmtree(plot_dir, True)

    def test_returned_path_is_a_directory(self, engine):
        engine.plot_settings = {"backend": "inline"}
        plot_dir = engine.make_figures()
        assert plot_dir is not None
        assert os.path.isdir(plot_dir)
        shutil.rmtree(plot_dir, True)

    def test_uses_provided_plot_dir(self, engine):
        engine.plot_settings = {"backend": "inline"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = engine.make_figures(plot_dir=tmp_dir)
            assert result == tmp_dir.replace(os.path.sep, "/")

    def test_non_inline_backend_returns_none(self, engine):
        engine.plot_settings = {"backend": "default"}
        result = engine.make_figures()
        assert result is None
        engine.plot_settings = {"backend": "inline"}

    def test_error_handler_called_on_octave_error(self):
        error_handler = MagicMock()
        with patch.object(OctaveEngine, "_create_repl", return_value=MagicMock()):
            eng = OctaveEngine(error_handler=error_handler, defer_startup=True)
        eng._has_startup = True
        eng._plot_settings = {
            "backend": "inline",
            "format": "png",
            "width": -1,
            "height": -1,
            "resolution": 0,
            "name": "Figure",
            "plot_dir": None,
        }
        with patch.object(eng, "eval", return_value="error: make_figures failed"):
            eng.make_figures()
        error_handler.assert_called_once()

    def test_raises_without_error_handler_on_octave_error(self):
        with patch.object(OctaveEngine, "_create_repl", return_value=MagicMock()):
            eng = OctaveEngine(defer_startup=True)
        eng._has_startup = True
        eng._plot_settings = {
            "backend": "inline",
            "format": "png",
            "width": -1,
            "height": -1,
            "resolution": 0,
            "name": "Figure",
            "plot_dir": None,
        }
        with patch.object(eng, "eval", return_value="error: make_figures failed"):
            with pytest.raises(Exception, match="Inline plot failed"):
                eng.make_figures()


# ---------------------------------------------------------------------------
# extract_figures
# ---------------------------------------------------------------------------


class TestExtractFigures:
    """Tests for OctaveEngine.extract_figures()."""

    def test_empty_dir_returns_empty_list(self, engine):
        engine.plot_settings = {"backend": "inline"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = engine.extract_figures(tmp_dir)
        assert result == []

    def test_extracts_single_png(self, engine):
        engine.plot_settings = {"backend": "inline"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            fname = os.path.join(tmp_dir, "Figure0.png")
            with open(fname, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
            result = engine.extract_figures(tmp_dir)
        assert len(result) == 1

    def test_extracts_multiple_pngs(self, engine):
        engine.plot_settings = {"backend": "inline"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            for i in range(3):
                fname = os.path.join(tmp_dir, f"Figure{i}.png")
                with open(fname, "wb") as f:
                    f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
            result = engine.extract_figures(tmp_dir)
        assert len(result) == 3

    def test_extracts_valid_svg(self, engine):
        engine.plot_settings = {"backend": "inline"}
        svg_content = (
            '<?xml version="1.0"?>'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            "</svg>"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            fname = os.path.join(tmp_dir, "Figure0.svg")
            with open(fname, "w") as f:
                f.write(svg_content)
            result = engine.extract_figures(tmp_dir)
        assert len(result) == 1

    def test_removes_dir_when_remove_true(self, engine):
        engine.plot_settings = {"backend": "inline"}
        tmp_dir = tempfile.mkdtemp()
        engine.extract_figures(tmp_dir, remove=True)
        assert not os.path.exists(tmp_dir)

    def test_preserves_dir_when_remove_false(self, engine):
        engine.plot_settings = {"backend": "inline"}
        with tempfile.TemporaryDirectory() as tmp_dir:
            engine.extract_figures(tmp_dir, remove=False)
            assert os.path.exists(tmp_dir)

    def test_error_handler_called_for_unreadable_pdf(self):
        error_handler = MagicMock()
        with patch.object(OctaveEngine, "_create_repl", return_value=MagicMock()):
            eng = OctaveEngine(error_handler=error_handler, defer_startup=True)
        eng._plot_settings = {
            "backend": "inline",
            "format": "pdf",
            "width": -1,
            "height": -1,
            "resolution": 0,
            "name": "Figure",
            "plot_dir": None,
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            fname = os.path.join(tmp_dir, "Figure0.pdf")
            with open(fname, "w") as f:
                f.write("placeholder")
            # Use patch to simulate PDF raising an error (os.chmod is unreliable on Windows).
            with patch("octave_kernel.kernel.PDF", side_effect=Exception("unreadable")):
                eng.extract_figures(tmp_dir)
        error_handler.assert_called_once()


# ---------------------------------------------------------------------------
# Private method helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_engine():
    """OctaveEngine with a mocked REPLWrapper — no real Octave process."""
    with patch.object(OctaveEngine, "_create_repl", return_value=MagicMock()):
        eng = OctaveEngine(defer_startup=True)
    return eng


_SVG_TEMPLATE = (
    '<?xml version="1.0"?>'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
    "</svg>"
)


# ---------------------------------------------------------------------------
# _startup
# ---------------------------------------------------------------------------


class TestStartup:
    """Tests for OctaveEngine._startup()."""

    def _run_startup(self, eng):
        """Run _startup with a patched eval that returns sensible defaults."""
        mock_eval = MagicMock(
            side_effect=lambda code, **kw: (
                "gnuplot" if code.strip() == "graphics_toolkit" else ""
            )
        )
        with patch.object(eng, "eval", mock_eval):
            eng._startup()
        return mock_eval

    def test_sets_has_startup(self, mock_engine):
        self._run_startup(mock_engine)
        assert mock_engine._has_startup is True

    def test_runs_more_off_command(self, mock_engine):
        mock_eval = self._run_startup(mock_engine)
        first_call_code = mock_eval.call_args_list[0][0][0]
        assert "more off" in first_call_code

    def test_sets_cwd_in_startup_command(self, mock_engine):
        mock_eval = self._run_startup(mock_engine)
        first_call_code = mock_eval.call_args_list[0][0][0]
        expected_cwd = os.getcwd().replace(os.path.sep, "/")
        assert expected_cwd in first_call_code

    def test_calls_addpath_with_package_directory(self, mock_engine):
        mock_eval = self._run_startup(mock_engine)
        all_code = " ".join(c[0][0] for c in mock_eval.call_args_list)
        assert "addpath" in all_code

    def test_addpath_points_to_octave_kernel_package(self, mock_engine):
        mock_eval = self._run_startup(mock_engine)
        addpath_calls = [
            c[0][0] for c in mock_eval.call_args_list if "addpath" in c[0][0]
        ]
        assert len(addpath_calls) == 1
        assert "octave_kernel" in addpath_calls[0]

    def test_applies_plot_settings_at_end(self, mock_engine):
        self._run_startup(mock_engine)
        # plot_settings setter populates _plot_settings with defaults.
        assert mock_engine._plot_settings is not None
        assert "backend" in mock_engine._plot_settings


# ---------------------------------------------------------------------------
# _handle_svg
# ---------------------------------------------------------------------------


class TestHandleSvg:
    """Tests for OctaveEngine._handle_svg()."""

    def test_returns_svg_object(self, engine, tmp_path):
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(_SVG_TEMPLATE.format(w=100, h=100))
        result = engine._handle_svg(str(svg_file))
        assert isinstance(result, SVG)

    def test_svg_data_contains_file_content(self, engine, tmp_path):
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(_SVG_TEMPLATE.format(w=100, h=100))
        result = engine._handle_svg(str(svg_file))
        assert "svg" in result.data

    def test_fix_svg_exception_is_caught_silently(self, engine, tmp_path):
        # _handle_svg swallows any exception from _fix_svg_size and returns
        # the SVG with its original data intact.
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(_SVG_TEMPLATE.format(w=100, h=100))
        with patch.object(
            OctaveEngine, "_fix_svg_size", side_effect=Exception("bad xml")
        ):
            result = engine._handle_svg(str(svg_file))
        assert isinstance(result, SVG)

    def test_handles_utf8_replacement_chars(self, engine, tmp_path):
        # Gnuplot can write bytes that are invalid UTF-8; they are replaced
        # by U+FFFD on read. Place the invalid bytes inside an XML comment
        # so the document stays well-formed after substitution.
        svg_file = tmp_path / "test.svg"
        svg_file.write_bytes(
            b'<?xml version="1.0"?>'
            b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50">'
            b"<!-- \xff\xfe -->"
            b"</svg>"
        )
        result = engine._handle_svg(str(svg_file))
        assert isinstance(result, SVG)


# ---------------------------------------------------------------------------
# _fix_svg_size
# ---------------------------------------------------------------------------


class TestFixSvgSize:
    """Tests for OctaveEngine._fix_svg_size()."""

    def _make_self(self, width=-1, height=-1):
        mock_self = MagicMock()
        mock_self.plot_settings = {"width": width, "height": height}
        return mock_self

    def test_sets_width_from_viewbox(self):
        result = OctaveEngine._fix_svg_size(
            self._make_self(), _SVG_TEMPLATE.format(w=400, h=300)
        )
        assert 'width="400px"' in result

    def test_sets_height_from_viewbox(self):
        result = OctaveEngine._fix_svg_size(
            self._make_self(), _SVG_TEMPLATE.format(w=400, h=300)
        )
        assert 'height="300px"' in result

    def test_custom_width_adjusts_height_proportionally(self):
        result = OctaveEngine._fix_svg_size(
            self._make_self(width=200), _SVG_TEMPLATE.format(w=400, h=300)
        )
        assert 'width="200px"' in result
        assert 'height="150px"' in result

    def test_custom_height_adjusts_width_proportionally(self):
        result = OctaveEngine._fix_svg_size(
            self._make_self(height=150), _SVG_TEMPLATE.format(w=400, h=300)
        )
        assert 'width="200px"' in result
        assert 'height="150px"' in result

    def test_custom_width_and_height_both_honored(self):
        result = OctaveEngine._fix_svg_size(
            self._make_self(width=200, height=100), _SVG_TEMPLATE.format(w=400, h=300)
        )
        assert 'width="200px"' in result
        assert 'height="100px"' in result

    def test_returns_xml_string(self):
        result = OctaveEngine._fix_svg_size(
            self._make_self(), _SVG_TEMPLATE.format(w=10, h=10)
        )
        assert isinstance(result, str)
        assert "<svg" in result


# ---------------------------------------------------------------------------
# _create_repl
# ---------------------------------------------------------------------------


class TestCreateRepl:
    """Tests for OctaveEngine._create_repl()."""

    def _repl_cmd(self, eng, **env):
        with patch("octave_kernel.kernel.REPLWrapper") as MockRepl:
            MockRepl.return_value = MagicMock()
            with patch.dict(os.environ, env):
                eng._create_repl()
        return MockRepl.call_args[0][0]

    def test_includes_no_gui_flag(self, mock_engine):
        assert "--no-gui" in self._repl_cmd(mock_engine)

    def test_includes_interactive_flag(self, mock_engine):
        assert "--interactive" in self._repl_cmd(mock_engine)

    def test_includes_quiet_flag(self, mock_engine):
        assert "--quiet" in self._repl_cmd(mock_engine)

    def test_includes_no_init_file_flag(self, mock_engine):
        assert "--no-init-file" in self._repl_cmd(mock_engine)

    def test_sets_term_env_to_dumb(self, mock_engine):
        with patch("octave_kernel.kernel.REPLWrapper") as MockRepl:
            MockRepl.return_value = MagicMock()
            mock_engine._create_repl()
        assert os.environ.get("TERM") == "dumb"

    def test_assigns_interrupt_handler_to_repl(self, mock_engine):
        with patch("octave_kernel.kernel.REPLWrapper") as MockRepl:
            MockRepl.return_value = MagicMock()
            repl = mock_engine._create_repl()
        assert repl.interrupt == mock_engine._interrupt

    def test_sets_delaybeforesend_to_none(self, mock_engine):
        with patch("octave_kernel.kernel.REPLWrapper") as MockRepl:
            MockRepl.return_value = MagicMock()
            repl = mock_engine._create_repl()
        assert repl.child.delaybeforesend is None

    def test_appends_octave_cli_options_env_var(self, mock_engine):
        cmd = self._repl_cmd(mock_engine, OCTAVE_CLI_OPTIONS="--no-gui")
        assert "--no-gui" in cmd

    def test_appends_instance_cli_options(self, mock_engine):
        mock_engine.cli_options = "--no-gui"
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OCTAVE_CLI_OPTIONS", None)
            cmd = self._repl_cmd(mock_engine)
        assert "--no-gui" in cmd


# ---------------------------------------------------------------------------
# _get_executable
# ---------------------------------------------------------------------------


class TestGetExecutable:
    """Tests for OctaveEngine._get_executable()."""

    def _call(self, env=None, which_map=None):
        """Call _get_executable on a throwaway MagicMock self."""
        env = env or {}
        which_map = which_map or {}

        def fake_which(name):
            return which_map.get(name)

        with patch.dict(os.environ, env, clear=False):
            # Remove OCTAVE_EXECUTABLE from env unless explicitly set.
            if "OCTAVE_EXECUTABLE" not in env:
                os.environ.pop("OCTAVE_EXECUTABLE", None)
            with patch("octave_kernel._utils.which", side_effect=fake_which):
                return OctaveEngine._get_executable(MagicMock())

    def test_uses_octave_executable_env_var(self):
        result = self._call(
            env={"OCTAVE_EXECUTABLE": "/usr/bin/octave"},
            which_map={"/usr/bin/octave": "/usr/bin/octave"},
        )
        assert result == "/usr/bin/octave"

    def test_uses_env_var_regardless_of_name(self):
        # The name check was removed; any OCTAVE_EXECUTABLE value is accepted.
        result = self._call(
            env={"OCTAVE_EXECUTABLE": "/usr/bin/python"},
            which_map={"/usr/bin/python": "/usr/bin/python"},
        )
        assert result == "/usr/bin/python"

    def test_finds_octave_first(self):
        result = self._call(
            which_map={"octave-cli": "/usr/bin/octave-cli", "octave": "/usr/bin/octave"}
        )
        assert result == "/usr/bin/octave"

    def test_falls_back_to_octave_cli_when_no_octave(self):
        result = self._call(which_map={"octave-cli": "/usr/bin/octave-cli"})
        assert result == "/usr/bin/octave-cli"

    def test_raises_when_nothing_found_and_no_flatpak(self):
        with pytest.raises(OSError, match="octave not found"):
            with patch(
                "octave_kernel._utils.subprocess.check_call",
                side_effect=FileNotFoundError,
            ):
                self._call(which_map={})

    def test_uses_flatpak_as_last_resort(self):
        with patch("octave_kernel._utils.subprocess.check_call", return_value=0):
            result = self._call(which_map={})
        assert "flatpak" in result

    def test_returns_forward_slashes(self):
        result = self._call(which_map={"octave": "/usr/bin/octave"})
        assert "\\" not in result


# ---------------------------------------------------------------------------
# _interrupt
# ---------------------------------------------------------------------------


class TestInterrupt:
    """Tests for OctaveEngine._interrupt()."""

    def test_calls_repl_wrapper_interrupt_on_posix(self, mock_engine):
        with patch.object(os, "name", "posix"):
            with patch.object(REPLWrapper, "interrupt", return_value="") as mock_int:
                mock_engine._interrupt()
        mock_int.assert_called_once_with(mock_engine.repl, continuation=False)

    def test_passes_continuation_flag_on_posix(self, mock_engine):
        with patch.object(os, "name", "posix"):
            with patch.object(REPLWrapper, "interrupt", return_value="") as mock_int:
                mock_engine._interrupt(continuation=True)
        mock_int.assert_called_once_with(mock_engine.repl, continuation=True)

    def test_warns_via_stream_handler_on_windows(self, mock_engine):
        stream_handler = MagicMock()
        mock_engine.stream_handler = stream_handler
        with patch.object(os, "name", "nt"):
            with patch.object(mock_engine, "_interrupt_expect", return_value=""):
                mock_engine._interrupt()
        stream_handler.assert_called_once()
        assert "Windows" in stream_handler.call_args[0][0]

    def test_warns_via_logger_when_no_stream_handler_on_windows(self, mock_engine):
        mock_engine.stream_handler = None
        mock_engine.logger = MagicMock()
        with patch.object(os, "name", "nt"):
            with patch.object(mock_engine, "_interrupt_expect", return_value=""):
                mock_engine._interrupt()
        mock_engine.logger.warning.assert_called_once()

    def test_calls_interrupt_expect_on_windows(self, mock_engine):
        mock_engine.stream_handler = MagicMock()
        with patch.object(os, "name", "nt"):
            with patch.object(
                mock_engine, "_interrupt_expect", return_value="out"
            ) as mock_ie:
                result = mock_engine._interrupt(silent=True)
        mock_ie.assert_called_once_with(True)
        assert result == "out"


# ---------------------------------------------------------------------------
# _interrupt_expect
# ---------------------------------------------------------------------------


class TestInterruptExpect:
    """Tests for OctaveEngine._interrupt_expect()."""

    _TOKEN = "a" * 32  # fixed token to substitute for uuid4().hex

    def _setup_child(self, mock_engine, pos_seq, before_seq):
        """Configure the mock child to yield pos/before values in sequence."""
        child = mock_engine.repl.child
        child.linesep = "\n"
        idx = [0]

        def expect_side_effect(_expects):
            i = idx[0]
            idx[0] += 1
            child.before = before_seq[i]
            return pos_seq[i]

        child.expect.side_effect = expect_side_effect
        mock_engine.repl.prompt_emit_cmd = None
        return child

    def test_returns_accumulated_lines_in_silent_mode(self, mock_engine):
        self._setup_child(mock_engine, [1, 0], ["line1", self._TOKEN])
        with patch("octave_kernel.kernel.uuid.uuid4") as mu:
            mu.return_value.hex = self._TOKEN
            result = mock_engine._interrupt_expect(silent=True)
        assert result == "line1"

    def test_multiple_lines_joined_with_newline(self, mock_engine):
        self._setup_child(mock_engine, [1, 1, 0], ["alpha", "beta", self._TOKEN])
        with patch("octave_kernel.kernel.uuid.uuid4") as mu:
            mu.return_value.hex = self._TOKEN
            result = mock_engine._interrupt_expect(silent=True)
        assert result == "alpha\nbeta"

    def test_streams_lines_in_non_silent_mode(self, mock_engine):
        stream_handler = MagicMock()
        mock_engine.stream_handler = stream_handler
        self._setup_child(mock_engine, [1, 0], ["output", self._TOKEN])
        with patch("octave_kernel.kernel.uuid.uuid4") as mu:
            mu.return_value.hex = self._TOKEN
            mock_engine._interrupt_expect(silent=False)
        stream_handler.assert_called_with("output")

    def test_partial_line_before_prompt_accumulated_in_silent_mode(self, mock_engine):
        # pos=0 but line != expected → partial line before prompt
        self._setup_child(mock_engine, [0, 0], ["partial", self._TOKEN])
        with patch("octave_kernel.kernel.uuid.uuid4") as mu:
            mu.return_value.hex = self._TOKEN
            result = mock_engine._interrupt_expect(silent=True)
        assert "partial" in result

    def test_empty_before_on_prompt_not_accumulated(self, mock_engine):
        # pos=0 with empty line (not the token, but len==0) → not appended
        self._setup_child(mock_engine, [0, 0], ["", self._TOKEN])
        with patch("octave_kernel.kernel.uuid.uuid4") as mu:
            mu.return_value.hex = self._TOKEN
            result = mock_engine._interrupt_expect(silent=True)
        assert result == ""

    def test_sends_expected_token_via_sendline(self, mock_engine):
        self._setup_child(mock_engine, [0], [self._TOKEN])
        with patch("octave_kernel.kernel.uuid.uuid4") as mu:
            mu.return_value.hex = self._TOKEN
            mock_engine._interrupt_expect(silent=True)
        mock_engine.repl.sendline.assert_called_once_with(f'disp("{self._TOKEN}");')


# ---------------------------------------------------------------------------
# _cleanup
# ---------------------------------------------------------------------------


class TestCleanup:
    """Tests for OctaveEngine._cleanup()."""

    def test_terminates_repl(self, mock_engine):
        mock_engine._cleanup()
        mock_engine.repl.terminate.assert_called_once()

    def test_handles_terminate_exception_gracefully(self, mock_engine):
        mock_engine.repl.terminate.side_effect = Exception("already dead")
        mock_engine.logger = MagicMock()
        mock_engine._cleanup()  # must not raise
        mock_engine.logger.debug.assert_called()

    def test_removes_octave_workspace_file(self, mock_engine):
        workspace = os.path.join(os.getcwd(), "octave-workspace")
        open(workspace, "w").close()
        try:
            mock_engine._cleanup()
            assert not os.path.exists(workspace)
        finally:
            if os.path.exists(workspace):
                os.remove(workspace)

    def test_does_nothing_when_no_workspace_file(self, mock_engine):
        workspace = os.path.join(os.getcwd(), "octave-workspace")
        assert not os.path.exists(workspace)
        mock_engine._cleanup()  # must not raise


# ---------------------------------------------------------------------------
# Issue #194 — pause() called from a function shows no prompt
# ---------------------------------------------------------------------------


def _is_sandboxed_octave() -> bool:
    """Return True when Octave runs inside Flatpak or Ubuntu Snap."""
    import subprocess

    from metakernel.pexpect import which

    exe = which("octave") or which("octave-cli") or ""
    if "snap" in exe:
        return True
    try:
        subprocess.check_call(
            ["flatpak", "info", "org.octave.Octave"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


_skip_if_sandboxed = pytest.mark.skipif(
    _is_sandboxed_octave(),
    reason="pause() stdin prompt unreliable inside Flatpak/Snap sandboxes",
)


class TestPauseFromFunction:
    """Regression tests for issue #194.

    When pause() is called from within a user-defined function, the stdin
    prompt marker arrives in pexpect's buffer preceded by a newline (left
    over after \r is consumed from prior output).  The STDIN_PROMPT_REGEX
    must use re.DOTALL so that the leading \\n does not prevent a match.
    """

    def test_stdin_prompt_regex_matches_with_leading_newline(self):
        """STDIN_PROMPT_REGEX must match when the buffer starts with \\n."""
        # This is the exact pattern that causes issue #194: after pexpect
        # processes the \r in "before pause\r\n", the buffer left behind is
        # "\nPaused, enter any value to continue__stdin_prompt>".  Without
        # re.DOTALL the leading \n prevents . from matching, so the regex
        # never fires and the REPL times out.
        buf = "\nPaused, enter any value to continue__stdin_prompt>"
        assert STDIN_PROMPT_REGEX.search(buf) is not None

    @_skip_if_sandboxed
    def test_pause_from_function_triggers_stdin_handler(self, engine):
        """pause() inside a function must invoke the stdin handler (issue #194)."""
        tmpdir = tempfile.mkdtemp()
        basename = "test_pause_from_fn_194"
        fname = os.path.join(tmpdir, f"{basename}.m")
        with open(fname, "w") as f:
            f.write(
                f"function {basename}()\n"
                "  disp('before pause')\n"
                "  pause()\n"
                "  disp('after pause')\n"
                "end\n"
            )

        stdin_calls: list[str] = []

        def fake_stdin(prompt: str) -> str:
            stdin_calls.append(prompt)
            return ""

        old_stdin = engine.stdin_handler
        engine.stdin_handler = fake_stdin
        try:
            engine.eval(f"addpath('{tmpdir}')", silent=True)
            engine.eval(f"{basename}()", timeout=15)
        finally:
            engine.stdin_handler = old_stdin
            shutil.rmtree(tmpdir, True)

        assert len(stdin_calls) == 1, (
            "stdin_handler was not called — pause() from a function did not "
            "produce a visible prompt (issue #194)"
        )
