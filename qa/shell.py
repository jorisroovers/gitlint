
# This code is mostly duplicated from the `gitlint.shell` module. We conciously duplicate this code as to not depend
# on gitlint internals for our integration testing framework.

import subprocess
from qa.utils import ustr, USE_SH_LIB, IS_PY2

if USE_SH_LIB:
    from sh import git, echo, gitlint  # pylint: disable=unused-import,no-name-in-module,import-error

    # import exceptions separately, this makes it a little easier to mock them out in the unit tests
    from sh import CommandNotFound, ErrorReturnCode, RunningCommand  # pylint: disable=import-error
else:

    class CommandNotFound(Exception):
        """ Exception indicating a command was not found during execution """
        pass

    class RunningCommand(object):
        pass

    class ShResult(RunningCommand):
        """ Result wrapper class. We use this to more easily migrate from using https://amoffat.github.io/sh/ to using
        the builtin subprocess module. """

        def __init__(self, full_cmd, stdout, stderr='', exitcode=0):
            self.full_cmd = full_cmd
            # TODO(jorisroovers): The 'sh' library by default will merge stdout and stderr. We mimic this behavior
            # for now until we fully remove the 'sh' library.
            self.stdout = stdout + ustr(stderr)
            self.stderr = stderr
            self.exit_code = exitcode

        def __str__(self):
            return self.stdout

    class ErrorReturnCode(ShResult, Exception):
        """ ShResult subclass for unexpected results (acts as an exception). """
        pass

    def git(*command_parts, **kwargs):
        return run_command("git", *command_parts, **kwargs)

    def echo(*command_parts, **kwargs):
        return run_command("echo", *command_parts, **kwargs)

    def gitlint(*command_parts, **kwargs):
        return run_command("gitlint", *command_parts, **kwargs)

    def run_command(command, *args, **kwargs):
        args = [command] + list(args)
        result = _exec(*args, **kwargs)
        # If we reach this point and the result has an exit_code that is larger than 0, this means that we didn't
        # get an exception (which is the default sh behavior for non-zero exit codes) and so the user is expecting
        # a non-zero exit code -> just return the entire result
        if hasattr(result, 'exit_code') and result.exit_code > 0:
            return result
        return ustr(result)

    def _exec(*args, **kwargs):
        if IS_PY2:
            no_command_error = OSError  # noqa pylint: disable=undefined-variable,invalid-name
        else:
            no_command_error = FileNotFoundError  # noqa pylint: disable=undefined-variable

        pipe = subprocess.PIPE
        popen_kwargs = {'stdout': pipe, 'stderr': pipe, 'shell': kwargs.get('_tty_out', False)}
        if '_cwd' in kwargs:
            popen_kwargs['cwd'] = kwargs['_cwd']
        if '_env' in kwargs:
            popen_kwargs['env'] = kwargs['_env']

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
