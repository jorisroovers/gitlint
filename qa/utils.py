import locale
import os
import platform

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
    gitlint_use_sh_lib_env = os.environ.get("GITLINT_QA_USE_SH_LIB", None)
    if gitlint_use_sh_lib_env:
        return gitlint_use_sh_lib_env == "1"
    return not PLATFORM_IS_WINDOWS


USE_SH_LIB = use_sh_library()

########################################################################################################################
# TERMINAL_ENCODING
# Encoding for reading gitlint command output


def getpreferredencoding():
    """Use local.getpreferredencoding() or fallback to UTF-8."""
    return locale.getpreferredencoding() or "UTF-8"


TERMINAL_ENCODING = getpreferredencoding()


########################################################################################################################
# FILE_ENCODING

# Encoding for reading/writing files within the tests, this is always UTF-8
FILE_ENCODING = "UTF-8"
