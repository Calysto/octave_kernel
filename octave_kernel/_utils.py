"""Utility functions for octave_kernel."""

from __future__ import annotations

import os
import subprocess

from metakernel.pexpect import which


def get_octave_executable(executable: str = "") -> str:
    """Find the Octave executable.

    Parameters
    ----------
    executable
        Explicit path or command to use. If empty, the function searches in
        order: ``OCTAVE_EXECUTABLE`` env var, ``octave`` on PATH,
        ``octave-cli`` on PATH, then the flatpak ``org.octave.Octave`` app.

    Returns
    -------
    str
        The resolved executable string.

    Raises
    ------
    OSError
        If no Octave executable can be found.
    """
    executable = executable or os.environ.get("OCTAVE_EXECUTABLE", "")
    if not executable:
        executable = which("octave") or ""
        if not executable:
            executable = which("octave-cli") or ""
        if not executable:
            # Try flatpak as a fallback.
            try:
                subprocess.check_call(
                    ["flatpak", "info", "org.octave.Octave"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                executable = "flatpak run org.octave.Octave"
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise OSError("octave not found, please see README") from None
    if not executable:
        raise OSError("octave not found, please see README")

    return executable.replace(os.path.sep, "/")


def is_sandboxed_octave(executable: str = "") -> bool:
    """Return True if Octave is running via flatpak or snap.

    Parameters
    ----------
    executable
        Explicit executable string to check. If empty, :func:`get_octave_executable`
        is called to resolve the executable.

    Returns
    -------
    bool
        True if the Octave executable is a flatpak or snap installation.
    """
    if not executable:
        try:
            executable = get_octave_executable()
        except OSError:
            return False
    return "flatpak" in executable or "snap" in executable
