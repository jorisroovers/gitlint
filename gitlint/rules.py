from abc import abstractmethod, ABCMeta
from gitlint.options import IntOption

import re


class Rule(object):
    """ Class representing gitlint rules. """
    options_spec = []
    id = []
    name = ""
    __metaclass__ = ABCMeta

    def __init__(self, opts={}):
        self.options = {}
        for op_spec in self.options_spec:
            self.options[op_spec.name] = op_spec
            actual_option = opts.get(op_spec.name)
            if actual_option:
                self.options[op_spec.name].set(actual_option)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name

    @abstractmethod
    def validate(self):
        pass


class MultilineRule(Rule):
    """ Class representing rules that act on multiple lines at once """
    pass


class LineRule(Rule):
    """ Class representing rules that act on a line by line basis """
    pass


class CommitMessageTitleRule(Rule):
    """ 'Tagging' class representing rules that apply to a commit message title """
    pass


class CommitMessageBodyRule(Rule):
    """ 'Tagging' class representing rules that apply to a commit message body """
    pass


class RuleViolation(object):
    def __init__(self, rule_id, message, content=None, line_nr=None):
        self.rule_id = rule_id
        self.line_nr = line_nr
        self.message = message
        self.content = content

    def __eq__(self, other):
        return self.rule_id == other.rule_id and \
               self.message == other.message and \
               self.content == other.content and \
               self.line_nr == other.line_nr

    def __str__(self):
        return "{0}: {1} {2}".format(self.line_nr, self.rule_id, self.message)

    def __repr__(self):
        return self.__str__()


class MaxLineLengthRule(LineRule):
    name = "max-line-length"
    id = "R1"
    options_spec = [IntOption('line-length', 80, "Max line length")]
    violation_message = "Line exceeds max length ({0}>{1})"

    def validate(self, line):
        max_length = self.options['line-length'].value
        if len(line) > max_length:
            return RuleViolation(self.id, self.violation_message.format(len(line), max_length), line)


class TrailingWhiteSpace(LineRule):
    name = "trailing-whitespace"
    id = "R2"
    violation_message = "Line has trailing whitespace"

    def validate(self, line):
        pattern = re.compile(r"\s$")
        if pattern.search(line):
            return RuleViolation(self.id, self.violation_message, line)


class HardTab(LineRule):
    name = "hard-tab"
    id = "R3"
    violation_message = "Line contains hard tab characters (\\t)"

    def validate(self, line):
        if "\t" in line:
            return RuleViolation(self.id, self.violation_message, line)


class TitleMaxLengthRule(MaxLineLengthRule, CommitMessageTitleRule):
    name = "title-max-length"
    id = "T1"
    violation_message = "Title exceeds max length ({0}>{1})"


class TitleTrailingWhitespace(TrailingWhiteSpace, CommitMessageTitleRule):
    name = "title-trailing-whitespace"
    id = "T2"
    violation_message = "Title has trailing whitespace"


class TitleHardTab(HardTab, CommitMessageTitleRule):
    name = "title-hard-tab"
    id = "T3"
    violation_message = "Title contains hard tab characters (\\t)"


class BodyMaxLengthRule(MaxLineLengthRule, CommitMessageBodyRule):
    name = "body-max-line-length"
    id = "B1"


class BodyTrailingWhitespace(TrailingWhiteSpace, CommitMessageBodyRule):
    name = "body-trailing-whitespace"
    id = "B2"


class BodyHardTab(HardTab, CommitMessageBodyRule):
    name = "body-hard-tab"
    id = "B3"
