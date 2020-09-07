from abc import abstractmethod
import os
import re

from gitlint.utils import ustr, sstr


def allow_none(func):
    """ Decorator that sets option value to None if the passed value is None, otherwise calls the regular set method """

    def wrapped(obj, value):
        if value is None:
            obj.value = None
        else:
            func(obj, value)

    return wrapped


class RuleOptionError(Exception):
    pass


class RuleOption(object):
    """ Base class representing a configurable part (i.e. option) of a rule (e.g. the max-length of the title-max-line
        rule).
        This class should not be used directly. Instead, use on the derived classes like StrOption, IntOption to set
        options of a particular type like int, str, etc.
    """

    def __init__(self, name, value, description):
        self.name = ustr(name)
        self.description = ustr(description)
        self.value = None
        self.set(value)

    @abstractmethod
    def set(self, value):
        """ Validates and sets the option's value """
        pass  # pragma: no cover

    def __str__(self):
        return sstr(self)  # pragma: no cover

    def __unicode__(self):
        return u"({0}: {1} ({2}))".format(self.name, self.value, self.description)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover

    def __eq__(self, other):
        return self.name == other.name and self.description == other.description and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)  # required for py2


class StrOption(RuleOption):
    @allow_none
    def set(self, value):
        self.value = ustr(value)


class IntOption(RuleOption):
    def __init__(self, name, value, description, allow_negative=False):
        self.allow_negative = allow_negative
        super(IntOption, self).__init__(name, value, description)

    def _raise_exception(self, value):
        if self.allow_negative:
            error_msg = u"Option '{0}' must be an integer (current value: '{1}')".format(self.name, value)
        else:
            error_msg = u"Option '{0}' must be a positive integer (current value: '{1}')".format(self.name, value)
        raise RuleOptionError(error_msg)

    @allow_none
    def set(self, value):
        try:
            self.value = int(value)
        except ValueError:
            self._raise_exception(value)

        if not self.allow_negative and self.value < 0:
            self._raise_exception(value)


class BoolOption(RuleOption):

    # explicit choice to not annotate with @allow_none: Booleans must be False or True, they cannot be unset.
    def set(self, value):
        value = ustr(value).strip().lower()
        if value not in ['true', 'false']:
            raise RuleOptionError(u"Option '{0}' must be either 'true' or 'false'".format(self.name))
        self.value = value == 'true'


class ListOption(RuleOption):
    """ Option that is either a given list or a comma-separated string that can be splitted into a list when being set.
    """

    @allow_none
    def set(self, value):
        if isinstance(value, list):
            the_list = value
        else:
            the_list = ustr(value).split(",")

        self.value = [ustr(item.strip()) for item in the_list if item.strip() != ""]


class PathOption(RuleOption):
    """ Option that accepts either a directory or both a directory and a file. """

    def __init__(self, name, value, description, type=u"dir"):
        self.type = type
        super(PathOption, self).__init__(name, value, description)

    @allow_none
    def set(self, value):
        value = ustr(value)

        error_msg = u""

        if self.type == 'dir':
            if not os.path.isdir(value):
                error_msg = u"Option {0} must be an existing directory (current value: '{1}')".format(self.name, value)
        elif self.type == 'file':
            if not os.path.isfile(value):
                error_msg = u"Option {0} must be an existing file (current value: '{1}')".format(self.name, value)
        elif self.type == 'both':
            if not os.path.isdir(value) and not os.path.isfile(value):
                error_msg = (u"Option {0} must be either an existing directory or file "
                             u"(current value: '{1}')").format(self.name, value)
        else:
            error_msg = u"Option {0} type must be one of: 'file', 'dir', 'both' (current: '{1}')".format(self.name,
                                                                                                         self.type)

        if error_msg:
            raise RuleOptionError(error_msg)

        self.value = os.path.realpath(value)


class RegexOption(RuleOption):

    @allow_none
    def set(self, value):
        try:
            self.value = re.compile(value, re.UNICODE)
        except (re.error, TypeError) as exc:
            raise RuleOptionError("Invalid regular expression: '{0}'".format(exc))

    def __deepcopy__(self, _):
        # copy.deepcopy() - used in rules.py - doesn't support copying regex objects prior to Python 3.7
        # To work around this, we have to implement this __deepcopy__ magic method
        # Relevant SO thread:
        # https://stackoverflow.com/questions/6279305/typeerror-cannot-deepcopy-this-pattern-object
        value = None if self.value is None else self.value.pattern
        return RegexOption(self.name, value, self.description)
