# This code is mostly duplicated from the `gitlint.shell` module. We consciously duplicate this code as to not depend
# on gitlint internals for our integration testing framework.

import asyncio
import queue
import subprocess
from qa.utils import USE_SH_LIB, DEFAULT_ENCODING

if USE_SH_LIB:
    from sh import git, echo, gitlint  # pylint: disable=unused-import,no-name-in-module,import-error

    gitlint = gitlint.bake(_unify_ttys=True, _tty_in=True)  # pylint: disable=invalid-name

    # import exceptions separately, this makes it a little easier to mock them out in the unit tests
    from sh import CommandNotFound, ErrorReturnCode, RunningCommand  # pylint: disable=import-error
else:

    class CommandNotFound(Exception):
        """Exception indicating a command was not found during execution"""

        pass

    class RunningCommand:
        pass

    class ShResult(RunningCommand):
        """Result wrapper class. We use this to more easily migrate from using https://amoffat.github.io/sh/ to using
        the builtin subprocess module."""

        def __init__(self, full_cmd, stdout, stderr="", exitcode=0):
            self.full_cmd = full_cmd
            # TODO(jorisroovers): The 'sh' library by default will merge stdout and stderr. We mimic this behavior
            # for now until we fully remove the 'sh' library.
            self._stdout = stdout + stderr
            self._stderr = stderr
            self.exit_code = exitcode

        def __str__(self):
            return self.stdout.decode(DEFAULT_ENCODING)

        def __unicode__(self):
            return self.stdout

        @property
        def stdout(self):
            return self._stdout

        @property
        def stderr(self):
            return self._stderr

        def __getattr__(self, p):  # pylint: disable=invalid-name
            # https://github.com/amoffat/sh/blob/e0ed8e244e9d973ef4e0749b2b3c2695e7b5255b/sh.py#L952=
            _unicode_methods = set(dir(str()))
            if p in _unicode_methods:
                return getattr(str(self), p)

            raise AttributeError

    class ErrorReturnCode(ShResult, Exception):
        """ShResult subclass for unexpected results (acts as an exception)."""

        pass

    def git(*command_parts, **kwargs):
        return run_command("git", *command_parts, **kwargs)

    def echo(*command_parts, **kwargs):
        return run_command("echo", *command_parts, **kwargs)

    def gitlint(*command_parts, **kwargs):
        return run_command("gitlint", *command_parts, **kwargs)

    def run_command(command, *args, **kwargs):
        args = [command] + list(args)
        return _exec(*args, **kwargs)

    def _exec(*args, **kwargs):
        popen_kwargs = {
            "stdout": asyncio.subprocess.PIPE,
            "stderr": asyncio.subprocess.PIPE,
            "stdin": asyncio.subprocess.PIPE,
            "shell": kwargs.get("_tty_out", False),
            "cwd": kwargs.get("_cwd", None),
            "env": kwargs.get("_env", None),
        }

        stdin = None
        if len(args) > 1 and isinstance(args[1], ShResult):
            stdin = args[1].stdout
            # pop args[1] from the array and use it as stdin
            args = list(args)
            args.pop(1)

        try:

            async def read_stream(p, stream, iofunc, q, timeout=0.3):
                line = bytearray()
                try:
                    while True:
                        char = await asyncio.wait_for(stream.read(1), timeout)
                        line += bytearray(char)
                        if char == b"\n":
                            decoded = line.decode(DEFAULT_ENCODING)
                            iofunc(decoded, q)
                            line = bytearray()
                except asyncio.TimeoutError:
                    decoded = line.decode(DEFAULT_ENCODING)
                    iofunc(decoded, q)

            async def write_stdin(p, q):
                # inputstr = await q.get()
                inputstr = await asyncio.wait_for(q.get(), 0.25)
                p.stdin.write(inputstr.encode(DEFAULT_ENCODING))
                await p.stdin.drain()

            if kwargs.get("_out", None):
                # redirect stderr to stdout (this will ensure we capture the last git output lines which are printed to stdout, not stderr)
                popen_kwargs["stderr"] = asyncio.subprocess.STDOUT

                async def start_process():
                    p = await asyncio.create_subprocess_exec(*args, **popen_kwargs)

                    q = asyncio.Queue()

                    await asyncio.gather(
                        # read_stream(p, p.stderr, kwargs["_out"], q),
                        read_stream(p, p.stdout, kwargs["_out"], q),
                    )
                    print("after gather1")
                    await asyncio.gather(write_stdin(p, q))
                    print("after gather2")

                    # Manually answer the prompt here, for some reason I can't get this to work via stdin
                    await asyncio.sleep(2)

                    await asyncio.gather(
                        read_stream(p, p.stdout, kwargs["_out"], q),
                    )
                    print("after gather 3")
                    await p.wait()
                    print("process finished")

                asyncio.run(start_process())
                return
            elif stdin:
                with subprocess.Popen(args, **popen_kwargs) as p:
                    result = p.communicate(stdin)
            else:
                with subprocess.Popen(args, **popen_kwargs) as p:
                    result = p.communicate()

        except FileNotFoundError as exc:
            raise CommandNotFound from exc

        exit_code = p.returncode
        stdout = result[0]
        stderr = result[1]  # 'sh' does not decode the stderr bytes to unicode
        full_cmd = "" if args is None else " ".join(args)

        # If not _ok_code is specified, then only a 0 exit code is allowed
        ok_exit_codes = kwargs.get("_ok_code", [0])

        if exit_code in ok_exit_codes:
            return ShResult(full_cmd, stdout, stderr, exit_code)

        # Unexpected error code => raise ErrorReturnCode
        raise ErrorReturnCode(full_cmd, stdout, stderr, p.returncode)
