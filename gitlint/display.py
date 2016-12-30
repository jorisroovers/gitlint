import codecs
import locale
from sys import stdout, stderr, version_info

# For some reason, python 2.x sometimes messes up with printing unicode chars to stdout/stderr
# This is mostly when there is a mismatch between the terminal encoding and the python encoding.
# This use-case is primarily triggered when piping input between commands, in particular our integration tests
# tend to trip over this.
if version_info[0] == 2:
    stdout = codecs.getwriter(locale.getpreferredencoding())(stdout)  # pylint: disable=invalid-name
    stderr = codecs.getwriter(locale.getpreferredencoding())(stderr)  # pylint: disable=invalid-name


class Display(object):
    """ Utility class to print stuff to an output stream (stdout by default) based on the config's verbosity """

    def __init__(self, lint_config):
        self.config = lint_config

    def _output(self, message, verbosity, exact, stream):
        """ Output a message if the config's verbosity is >= to the given verbosity. If exact == True, the message
        will only be outputted if the given verbosity exactly matches the config's verbosity. """
        if exact:
            if self.config.verbosity == verbosity:
                stream.write(message + "\n")
        else:
            if self.config.verbosity >= verbosity:
                stream.write(message + "\n")

    def v(self, message, exact=False):  # pylint: disable=invalid-name
        self._output(message, 1, exact, stdout)

    def vv(self, message, exact=False):  # pylint: disable=invalid-name
        self._output(message, 2, exact, stdout)

    def vvv(self, message, exact=False):  # pylint: disable=invalid-name
        self._output(message, 3, exact, stdout)

    def e(self, message, exact=False):  # pylint: disable=invalid-name
        self._output(message, 1, exact, stderr)

    def ee(self, message, exact=False):  # pylint: disable=invalid-name
        self._output(message, 2, exact, stderr)

    def eee(self, message, exact=False):  # pylint: disable=invalid-name
        self._output(message, 3, exact, stderr)
