import os
import re
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from gitlint.exception import GitlintError


def allow_none(func):
    """Decorator that sets option value to None if the passed value is None, otherwise calls the regular set method"""

    def wrapped(obj, value):
        if value is None:
            obj.value = None
        else:
            func(obj, value)

    return wrapped


class RuleOptionError(GitlintError):
    pass


@dataclass
class RuleOption:
    """Base class representing a configurable part (i.e. option) of a rule (e.g. the max-length of the title-max-line
    rule).
    This class should not be used directly. Instead, use on the derived classes like StrOption, IntOption to set
    options of a particular type like int, str, etc.
    """

    name: str
    value: Any
    description: str

    def __post_init__(self):
        self.set(self.value)

    @abstractmethod
    def set(self, value):
        """Validates and sets the option's value"""

    def __str__(self):
        return f"({self.name}: {self.value} ({self.description}))"


@dataclass
class StrOption(RuleOption):
    @allow_none
    def set(self, value):
        self.value = str(value)


@dataclass
class IntOption(RuleOption):
    allow_negative: bool = False

    def _raise_exception(self, value):
        if self.allow_negative:
            error_msg = f"Option '{self.name}' must be an integer (current value: '{value}')"
        else:
            error_msg = f"Option '{self.name}' must be a positive integer (current value: '{value}')"
        raise RuleOptionError(error_msg)

    @allow_none
    def set(self, value):
        try:
            self.value = int(value)
        except ValueError:
            self._raise_exception(value)

        if not self.allow_negative and self.value < 0:
            self._raise_exception(value)


@dataclass
class BoolOption(RuleOption):
    # explicit choice to not annotate with @allow_none: Booleans must be False or True, they cannot be unset.
    def set(self, value):
        value = str(value).strip().lower()
        if value not in ["true", "false"]:
            raise RuleOptionError(f"Option '{self.name}' must be either 'true' or 'false'")
        self.value = value == "true"


@dataclass
class ListOption(RuleOption):
    """Option that is either a given list or a comma-separated string that can be split into a list when being set."""

    @allow_none
    def set(self, value):
        if isinstance(value, list):
            the_list = value
        else:
            the_list = str(value).split(",")

        self.value = [str(item.strip()) for item in the_list if item.strip() != ""]


@dataclass
class PathOption(RuleOption):
    """Option that accepts either a directory or both a directory and a file."""

    type: str = "dir"

    @allow_none
    def set(self, value):
        value = str(value)

        error_msg = ""

        if self.type == "dir":
            if not os.path.isdir(value):
                error_msg = f"Option {self.name} must be an existing directory (current value: '{value}')"
        elif self.type == "file":
            if not os.path.isfile(value):
                error_msg = f"Option {self.name} must be an existing file (current value: '{value}')"
        elif self.type == "both":
            if not os.path.isdir(value) and not os.path.isfile(value):
                error_msg = (
                    f"Option {self.name} must be either an existing directory or file (current value: '{value}')"
                )
        else:
            error_msg = f"Option {self.name} type must be one of: 'file', 'dir', 'both' (current: '{self.type}')"

        if error_msg:
            raise RuleOptionError(error_msg)

        self.value = os.path.realpath(value)


@dataclass
class RegexOption(RuleOption):
    @allow_none
    def set(self, value):
        try:
            self.value = re.compile(value, re.UNICODE)
        except (re.error, TypeError) as exc:
            raise RuleOptionError(f"Invalid regular expression: '{exc}'") from exc

    def __deepcopy__(self, _):
        # copy.deepcopy() - used in rules.py - doesn't support copying regex objects prior to Python 3.7
        # To work around this, we have to implement this __deepcopy__ magic method
        # Relevant SO thread:
        # https://stackoverflow.com/questions/6279305/typeerror-cannot-deepcopy-this-pattern-object
        value = None if self.value is None else self.value.pattern
        return RegexOption(self.name, value, self.description)
