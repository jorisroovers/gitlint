class Display(object):
    """ Utility class to print stuff to an output stream (stdout by default) based on the config's verbosity """

    def __init__(self, lint_config):
        self.config = lint_config

    def _output(self, message, verbosity, exact):
        """ Output a message if the config's verbosity is >= to the given verbosity. If exact == True, the message
        will only be outputted if the given verbosity exactly matches the config's verbosity. """
        if exact:
            if self.config.verbosity == verbosity:
                print message
        else:
            if self.config.verbosity >= verbosity:
                print(message)

    def v(self, message, exact=False):
        self._output(message, 1, exact)

    def vv(self, message, exact=False):
        self._output(message, 2, exact)

    def vvv(self, message, exact=False):
        self._output(message, 3, exact)
