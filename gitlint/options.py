from abc import abstractmethod
import os

from gitlint.utils import ustr, sstr


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


class StrOption(RuleOption):
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

    def set(self, value):
        try:
            self.value = int(value)
        except ValueError:
            self._raise_exception(value)

        if not self.allow_negative and self.value < 0:
            self._raise_exception(value)


class BoolOption(RuleOption):
    def set(self, value):
        value = ustr(value).strip().lower()
        if value not in ['true', 'false']:
            raise RuleOptionError(u"Option '{0}' must be either 'true' or 'false'".format(self.name))
        self.value = value == 'true'


class ListOption(RuleOption):
    """ Option that is either a given list or a comma-separated string that can be splitted into a list when being set.
    """

    def set(self, value):
        if isinstance(value, list):
            the_list = value
        else:
            the_list = ustr(value).split(",")

        self.value = [ustr(item.strip()) for item in the_list if item.strip() != ""]


class DirectoryOption(RuleOption):
    def set(self, value):
        value = ustr(value)
        if not os.path.isdir(value):
            msg = u"Option {0} must be an existing directory (current value: '{1}')".format(self.name, value)
            raise RuleOptionError(msg)
        self.value = os.path.abspath(value)
