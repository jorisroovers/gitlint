
"""
This module implements a shim for the 'sh' library, mainly for use on Windows (sh is not supported on Windows).
We might consider removing the 'sh' dependency alltogether in the future, but 'sh' does provide a few
capabilities wrt dealing with more edge-case environments on *nix systems that might be useful.
"""

import subprocess
import sys
from gitlint.utils import ustr, USE_SH_LIB

if USE_SH_LIB:
    from sh import git  # pylint: disable=unused-import,import-error
    # import exceptions separately, this makes it a little easier to mock them out in the unit tests
    from sh import CommandNotFound, ErrorReturnCode  # pylint: disable=import-error
else:

    class CommandNotFound(Exception):
        """ Exception indicating a command was not found during execution """
        pass

    class ShResult(object):
        """ Result wrapper class. We use this to more easily migrate from using https://amoffat.github.io/sh/ to using
        the builtin subprocess. module """

        def __init__(self, full_cmd, stdout, stderr='', exitcode=0):
            self.full_cmd = full_cmd
            self.stdout = stdout
            self.stderr = stderr
            self.exit_code = exitcode

        def __str__(self):
            return self.stdout

    class ErrorReturnCode(ShResult, Exception):
        """ ShResult subclass for unexpected results (acts as an exception). """
        pass

    def git(*command_parts, **kwargs):
        """ Git shell wrapper.
        Implemented as separate function here, so we can do a 'sh' style imports:
        `from shell import git`
        """
        args = ['git'] + list(command_parts)
        return _exec(*args, **kwargs)

    def _exec(*args, **kwargs):
        if sys.version_info[0] == 2:
            no_command_error = OSError  # noqa pylint: disable=undefined-variable,invalid-name
        else:
            no_command_error = FileNotFoundError  # noqa pylint: disable=undefined-variable

        pipe = subprocess.PIPE
        popen_kwargs = {'stdout': pipe, 'stderr': pipe, 'shell': kwargs['_tty_out']}
        if '_cwd' in kwargs:
            popen_kwargs['cwd'] = kwargs['_cwd']

        try:
            p = subprocess.Popen(args, **popen_kwargs)
            result = p.communicate()
        except no_command_error:
            raise CommandNotFound

        exit_code = p.returncode
        stdout = ustr(result[0])
        stderr = result[1]  # 'sh' does not decode the stderr bytes to unicode
        full_cmd = '' if args is None else ' '.join(args)

        # If not _ok_code is specified, then only a 0 exit code is allowed
        ok_exit_codes = kwargs.get('_ok_code', [0])

        if exit_code in ok_exit_codes:
            return ShResult(full_cmd, stdout, stderr, exit_code)

        # Unexpected error code => raise ErrorReturnCode
        raise ErrorReturnCode(full_cmd, stdout, stderr, p.returncode)
