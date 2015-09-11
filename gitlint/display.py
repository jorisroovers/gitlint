from sys import stdout, stderr


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

    def v(self, message, exact=False):
        self._output(message, 1, exact, stdout)

    def vv(self, message, exact=False):
        self._output(message, 2, exact, stdout)

    def vvv(self, message, exact=False):
        self._output(message, 3, exact, stdout)

    def e(self, message, exact=False):
        self._output(message, 1, exact, stderr)

    def ee(self, message, exact=False):
        self._output(message, 2, exact, stderr)

    def eee(self, message, exact=False):
        self._output(message, 3, exact, stderr)
