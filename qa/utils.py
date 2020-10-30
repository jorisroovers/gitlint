# pylint: disable=bad-option-value,unidiomatic-typecheck,undefined-variable,no-else-return
import platform
import os

import locale

########################################################################################################################
# PLATFORM_IS_WINDOWS


def platform_is_windows():
    return "windows" in platform.system().lower()


PLATFORM_IS_WINDOWS = platform_is_windows()

########################################################################################################################
# USE_SH_LIB
# Determine whether to use the `sh` library
# On windows we won't want to use the sh library since it's not supported - instead we'll use our own shell module.
# However, we want to be able to overwrite this behavior for testing using the GITLINT_QA_USE_SH_LIB env var.


def use_sh_library():
    gitlint_use_sh_lib_env = os.environ.get('GITLINT_QA_USE_SH_LIB', None)
    if gitlint_use_sh_lib_env:
        return gitlint_use_sh_lib_env == "1"
    return not PLATFORM_IS_WINDOWS


USE_SH_LIB = use_sh_library()

########################################################################################################################
# DEFAULT_ENCODING


def getpreferredencoding():
    """ Modified version of local.getpreferredencoding() that takes into account LC_ALL, LC_CTYPE, LANG env vars
        on windows and falls back to UTF-8. """
    default_encoding = locale.getpreferredencoding() or "UTF-8"

    # On Windows, we mimic git/linux by trying to read the LC_ALL, LC_CTYPE, LANG env vars manually
    # (on Linux/MacOS the `getpreferredencoding()` call will take care of this).
    # We fallback to UTF-8
    if PLATFORM_IS_WINDOWS:
        default_encoding = "UTF-8"
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

    return default_encoding


DEFAULT_ENCODING = getpreferredencoding()
