# pylint: disable=bad-option-value,unidiomatic-typecheck,undefined-variable,no-else-return
import platform
import sys
import os

from locale import getpreferredencoding

DEFAULT_ENCODING = getpreferredencoding() or "UTF-8"
LOG_FORMAT = '%(levelname)s: %(name)s %(message)s'

# On windows we won't want to use the sh library since it's not supported - instead we'll use our own shell module.
# However, we want to be able to overwrite this behavior for testing using the GITLINT_USE_SH_LIB env var.
PLATFORM_IS_WINDOWS = "windows" in platform.system().lower()
GITLINT_USE_SH_LIB_ENV = os.environ.get('GITLINT_USE_SH_LIB', None)
if GITLINT_USE_SH_LIB_ENV:
    USE_SH_LIB = (GITLINT_USE_SH_LIB_ENV == "1")
else:
    USE_SH_LIB = not PLATFORM_IS_WINDOWS


def ustr(obj):
    """ Python 2 and 3 utility method that converts an obj to unicode in python 2 and to a str object in python 3"""
    if sys.version_info[0] == 2:
        # If we are getting a string, then do an explicit decode
        # else, just call the unicode method of the object
        if type(obj) in [str, basestring]:  # pragma: no cover # noqa
            return unicode(obj, DEFAULT_ENCODING)  # pragma: no cover # noqa
        else:
            return unicode(obj)  # pragma: no cover # noqa
    else:
        if type(obj) in [bytes]:
            return obj.decode(DEFAULT_ENCODING)
        else:
            return str(obj)


def sstr(obj):
    """ Python 2 and 3 utility method that converts an obj to a DEFAULT_ENCODING encoded string in python 2
    and to unicode in python 3.
    Especially useful for implementing __str__ methods in python 2: http://stackoverflow.com/a/1307210/381010"""
    if sys.version_info[0] == 2:
        return unicode(obj).encode(DEFAULT_ENCODING)  # pragma: no cover # noqa
    else:
        return obj  # pragma: no cover
