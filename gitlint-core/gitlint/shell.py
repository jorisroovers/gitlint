"""
This module implements a shim for the 'sh' library, mainly for use on Windows (sh is not supported on Windows).
We might consider removing the 'sh' dependency altogether in the future, but 'sh' does provide a few
capabilities wrt dealing with more edge-case environments on *nix systems that are useful.
"""

import subprocess

from gitlint.utils import TERMINAL_ENCODING, USE_SH_LIB


def shell(cmd):
    """Convenience function that opens a given command in a shell. Does not use 'sh' library."""
    with subprocess.Popen(cmd, shell=True) as p:
        p.communicate()


if USE_SH_LIB:
    # import exceptions separately, this makes it a little easier to mock them out in the unit tests
    from sh import (
        CommandNotFound,
        ErrorReturnCode,
        git,
    )
else:

    class CommandNotFound(Exception):
        """Exception indicating a command was not found during execution"""

    class ShResult:
        """Result wrapper class. We use this to more easily migrate from using https://amoffat.github.io/sh/ to using
        the builtin subprocess module"""

        def __init__(self, full_cmd, stdout, stderr="", exitcode=0):
            self.full_cmd = full_cmd
            self.stdout = stdout
            self.stderr = stderr
            self.exit_code = exitcode

        def __str__(self):
            return self.stdout

    class ErrorReturnCode(ShResult, Exception):
        """ShResult subclass for unexpected results (acts as an exception)."""

    def git(*command_parts, **kwargs):
        """Git shell wrapper.
        Implemented as separate function here, so we can do a 'sh' style imports:
        `from shell import git`
        """
        args = ["git", *list(command_parts)]
        return _exec(*args, **kwargs)

    def _exec(*args, **kwargs):
        pipe = subprocess.PIPE
        popen_kwargs = {"stdout": pipe, "stderr": pipe, "shell": kwargs.get("_tty_out", False)}
        if "_cwd" in kwargs:
            popen_kwargs["cwd"] = kwargs["_cwd"]

        try:
            with subprocess.Popen(args, **popen_kwargs) as p:
                result = p.communicate()
        except FileNotFoundError as e:
            raise CommandNotFound from e

        exit_code = p.returncode
        stdout = result[0].decode(TERMINAL_ENCODING)
        stderr = result[1]  # 'sh' does not decode the stderr bytes to unicode
        full_cmd = "" if args is None else " ".join(args)

        # If not _ok_code is specified, then only a 0 exit code is allowed
        ok_exit_codes = kwargs.get("_ok_code", [0])

        if exit_code in ok_exit_codes:
            return ShResult(full_cmd, stdout, stderr, exit_code)

        # Unexpected error code => raise ErrorReturnCode
        raise ErrorReturnCode(full_cmd, stdout, stderr, p.returncode)
