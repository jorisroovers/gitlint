import subprocess
from locale import getpreferredencoding
DEFAULT_ENCODING = getpreferredencoding() or "UTF-8"


class ShResult(object):

    exit_code = None
    stdout = None
    stderr = None
    full_cmd = None

    def __init__(self, stdout, stderr='', exitcode=0, args=None):
        self.exit_code = exitcode
        self.stdout = stdout
        self.stderr = stderr
        self.full_cmd = '' if args is None else ' '.join(args)

    def __str__(self):
        return self.stdout


def git(*command_parts, **kwargs):
    args = ['git'] + list(command_parts)
    return _exec(*args, **kwargs)


def _exec(*args, **kwargs):
    pipe = subprocess.PIPE
    popen_kwargs = {'stdout': pipe, 'stderr': pipe, 'shell': False}
    if '_cwd' in kwargs:
        popen_kwargs['cwd'] = kwargs['_cwd']
    p = subprocess.Popen(args, **popen_kwargs)
    result = p.communicate()
    exit_code = p.returncode
    if exit_code == 0:
        return result[0].decode(DEFAULT_ENCODING)
    stdout = result[0].decode(DEFAULT_ENCODING)
    stderr = result[1].decode(DEFAULT_ENCODING)
    return ShResult(stdout, stderr, p.returncode, args)
