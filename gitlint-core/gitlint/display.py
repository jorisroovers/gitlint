from dataclasses import dataclass
from sys import stderr, stdout
from typing import TextIO

from gitlint.config import LintConfig


@dataclass
class Display:
    """Utility class to print stuff to an output stream (stdout by default) based on the config's verbosity"""

    config: LintConfig

    def _output(self, message: str, verbosity: int, exact: bool, stream: TextIO) -> None:
        """Output a message if the config's verbosity is >= to the given verbosity. If exact == True, the message
        will only be outputted if the given verbosity exactly matches the config's verbosity."""
        if exact:
            if self.config.verbosity == verbosity:
                stream.write(message + "\n")
        else:
            if self.config.verbosity >= verbosity:
                stream.write(message + "\n")

    def v(self, message: str, exact: bool = False) -> None:
        self._output(message, 1, exact, stdout)

    def vv(self, message: str, exact: bool = False) -> None:
        self._output(message, 2, exact, stdout)

    def vvv(self, message: str, exact: bool = False) -> None:
        self._output(message, 3, exact, stdout)

    def e(self, message: str, exact: bool = False) -> None:
        self._output(message, 1, exact, stderr)

    def ee(self, message: str, exact: bool = False) -> None:
        self._output(message, 2, exact, stderr)

    def eee(self, message: str, exact: bool = False) -> None:
        self._output(message, 3, exact, stderr)
