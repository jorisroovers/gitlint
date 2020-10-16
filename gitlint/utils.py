# pylint: disable=bad-option-value,unidiomatic-typecheck,undefined-variable,no-else-return
import codecs
import platform
import sys
import os

import locale

# Note: While we can easily inline the logic related to the constants set in this module, we deliberately create
# small functions that encapsulate that logic as this enables easy unit testing. In particular, by creating functions
# we can easily mock the dependencies during testing, which is not possible if the code is not enclosed in a function
# and just executed at import-time.

########################################################################################################################
LOG_FORMAT = '%(levelname)s: %(name)s %(message)s'

########################################################################################################################
# PLATFORM_IS_WINDOWS


def platform_is_windows():
    return "windows" in platform.system().lower()


PLATFORM_IS_WINDOWS = platform_is_windows()

########################################################################################################################
# IS_PY2


def is_py2():
    return sys.version_info[0] == 2


IS_PY2 = is_py2()

########################################################################################################################
# USE_SH_LIB
# Determine whether to use the `sh` library
# On windows we won't want to use the sh library since it's not supported - instead we'll use our own shell module.
# However, we want to be able to overwrite this behavior for testing using the GITLINT_USE_SH_LIB env var.


def use_sh_library():
    gitlint_use_sh_lib_env = os.environ.get('GITLINT_USE_SH_LIB', None)
    if gitlint_use_sh_lib_env:
        return gitlint_use_sh_lib_env == "1"
    return not PLATFORM_IS_WINDOWS


USE_SH_LIB = use_sh_library()

########################################################################################################################
# DEFAULT_ENCODING


def getpreferredencoding():
    """ Modified version of local.getpreferredencoding() that takes into account LC_ALL, LC_CTYPE, LANG env vars
        on windows and falls back to UTF-8. """
    fallback_encoding = "UTF-8"
    default_encoding = locale.getpreferredencoding() or fallback_encoding

    # On Windows, we mimic git/linux by trying to read the LC_ALL, LC_CTYPE, LANG env vars manually
    # (on Linux/MacOS the `getpreferredencoding()` call will take care of this).
    # We fallback to UTF-8
    if PLATFORM_IS_WINDOWS:
        default_encoding = fallback_encoding
        for env_var in ["LC_ALL", "LC_CTYPE", "LANG"]:
            encoding = os.environ.get(env_var, False)
            if encoding:
                # Support dotted (C.UTF-8) and non-dotted (C or UTF-8) charsets:
                # If encoding contains a dot: split and use second part, otherwise use everything
                dot_index = encoding.find(".")
                if dot_index != -1:
                    default_encoding = encoding[dot_index + 1:]
                else:
                    default_encoding = encoding
                break

        # We've determined what encoding the user *wants*, let's now check if it's actually a valid encoding on the
        # system. If not, fallback to UTF-8.
        # This scenario is fairly common on Windows where git sets LC_CTYPE=C when invoking the commit-msg hook, which
        # is not a valid encoding in Python on Windows.
        try:
            codecs.lookup(default_encoding)
        except LookupError:
            default_encoding = fallback_encoding

    return default_encoding


DEFAULT_ENCODING = getpreferredencoding()

########################################################################################################################
# Unicode utility functions


def ustr(obj):
    """ Python 2 and 3 utility method that converts an obj to unicode in python 2 and to a str object in python 3"""
    if IS_PY2:
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
    if IS_PY2:
        # For lists and tuples in python2, remove unicode string representation characters.
        # i.e. ensure lists are printed as ['a', 'b'] and not [u'a', u'b']
        if type(obj) in [list]:
            return [sstr(item) for item in obj] # pragma: no cover # noqa
        elif type(obj) in [tuple]:
            return tuple(sstr(item) for item in obj) # pragma: no cover # noqa

        return unicode(obj).encode(DEFAULT_ENCODING)  # pragma: no cover # noqa
    else:
        return obj  # pragma: no cover
