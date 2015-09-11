from abc import abstractmethod


class RuleOptionError(Exception):
    pass


class RuleOption(object):
    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

    @abstractmethod
    def set(self, value):
        """ Validates and sets the option's value """
        pass  # pragma: no cover

    def __str__(self):
        return "({}: {} ({}))".format(self.name, self.value, self.description)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class IntOption(RuleOption):
    def __init__(self, name, value, description, allow_negative=False):
        super(IntOption, self).__init__(name, value, description)
        self.allow_negative = allow_negative

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


class ListOption(RuleOption):
    def __init__(self, name, value, description):
        super(ListOption, self).__init__(name, value, description)

    def set(self, value):
        self.value = [item.strip() for item in str(value).split(",")]
