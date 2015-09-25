from abc import abstractmethod


class RuleOptionError(Exception):
    pass


class RuleOption(object):
    def __init__(self, name, value, description):
        self.name = name
        self.description = description
        self.value = None
        self.set(value)

    @abstractmethod
    def set(self, value):
        """ Validates and sets the option's value """
        pass  # pragma: no cover

    def __str__(self):
        return "({}: {} ({}))".format(self.name, self.value, self.description)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class StrOption(RuleOption):
    def set(self, value):
        self.value = str(value)


class IntOption(RuleOption):
    def __init__(self, name, value, description, allow_negative=False):
        self.allow_negative = allow_negative
        super(IntOption, self).__init__(name, value, description)

    def _raise_exception(self, value):
        if self.allow_negative:
            error_msg = "Option '{0}' must be an integer (current value: '{1}')".format(self.name, value)
        else:
            error_msg = "Option '{0}' must be a positive integer (current value: '{1}')".format(self.name, value)
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
        value = str(value).strip().lower()
        if value not in ['true', 'false']:
            raise RuleOptionError("Option '{}' must be either 'true' or 'false'".format(self.name))
        self.value = value == 'true'


class ListOption(RuleOption):
    def set(self, value):
        if isinstance(value, list):
            self.value = value
        else:
            self.value = [item.strip() for item in str(value).split(",") if item.strip() != ""]
