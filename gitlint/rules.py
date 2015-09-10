from abc import abstractmethod, ABCMeta
from gitlint.options import IntOption, ListOption

import copy
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
            self.options[op_spec.name] = copy.deepcopy(op_spec)
            actual_option = opts.get(op_spec.name)
            if actual_option:
                self.options[op_spec.name].set(actual_option)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name

    @abstractmethod
    def validate(self):
        pass


class MultiLineRule(Rule):
    """ Class representing rules that act on multiple lines at once """
    pass


class LineRule(Rule):
    """ Class representing rules that act on a line by line basis """
    pass


class CommitMessageTitleRule(LineRule):
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
        equal = self.rule_id == other.rule_id and self.message == other.message
        equal = equal and self.content == other.content and self.line_nr == other.line_nr
        return equal

    def __str__(self):
        return "{}: {} {}: \"{}\"".format(self.line_nr, self.rule_id, self.message, self.content)

    def __repr__(self):
        return self.__str__()


class MaxLineLength(LineRule):
    name = "max-line-length"
    id = "R1"
    options_spec = [IntOption('line-length', 80, "Max line length")]
    violation_message = "Line exceeds max length ({0}>{1})"

    def validate(self, line):
        max_length = self.options['line-length'].value
        if len(line) > max_length:
            return [RuleViolation(self.id, self.violation_message.format(len(line), max_length), line)]


class TrailingWhiteSpace(LineRule):
    name = "trailing-whitespace"
    id = "R2"
    violation_message = "Line has trailing whitespace"

    def validate(self, line):
        pattern = re.compile(r"\s$")
        if pattern.search(line):
            return [RuleViolation(self.id, self.violation_message, line)]


class HardTab(LineRule):
    name = "hard-tab"
    id = "R3"
    violation_message = "Line contains hard tab characters (\\t)"

    def validate(self, line):
        if "\t" in line:
            return [RuleViolation(self.id, self.violation_message, line)]


class LineMustNotContainWord(LineRule):
    """ Violation if a line contains one of a list of words (NOTE: using a word in the list inside another word is not a
    violation, e.g: WIPING is not a violation if 'WIP' is a word that is not allowed.) """
    name = "line-must-not-contain"
    id = "R5"
    options_spec = [ListOption('words', [], "Comma seperated list of words that should not be found")]
    violation_message = "Line contains {0}"

    def validate(self, line):
        strings = self.options['words'].value
        violations = []
        for string in strings:
            regex = re.compile(r"\b%s\b" % string.lower(), re.I)
            match = regex.search(line.lower())
            if match:
                violations.append(RuleViolation(self.id, self.violation_message.format(string), line))
        return violations if violations else None


class TitleMaxLength(MaxLineLength, CommitMessageTitleRule):
    name = "title-max-length"
    id = "T1"
    violation_message = "Title exceeds max length ({0}>{1})"


class TitleTrailingWhitespace(TrailingWhiteSpace, CommitMessageTitleRule):
    name = "title-trailing-whitespace"
    id = "T2"
    violation_message = "Title has trailing whitespace"


class TitleTrailingPunctuation(CommitMessageTitleRule):
    name = "title-trailing-punctuation"
    id = "T3"

    def validate(self, line):
        punctuation_marks = '?:!.,;'
        for punctuation_mark in punctuation_marks:
            if line.endswith(punctuation_mark):
                return [RuleViolation(self.id, "Title has trailing punctuation ({0})".format(punctuation_mark), line)]


class TitleHardTab(HardTab, CommitMessageTitleRule):
    name = "title-hard-tab"
    id = "T4"
    violation_message = "Title contains hard tab characters (\\t)"


class TitleMustNotContainWord(LineMustNotContainWord, CommitMessageTitleRule):
    name = "title-must-not-contain-word"
    id = "T5"
    options_spec = [ListOption('words', ['WIP'], "Must not contain word")]
    violation_message = "Title contains the word '{0}' (case-insensitive)"


class BodyMaxLength(MaxLineLength, CommitMessageBodyRule):
    name = "body-max-line-length"
    id = "B1"


class BodyTrailingWhitespace(TrailingWhiteSpace, CommitMessageBodyRule):
    name = "body-trailing-whitespace"
    id = "B2"


class BodyHardTab(HardTab, CommitMessageBodyRule):
    name = "body-hard-tab"
    id = "B3"


class BodyFirstLineEmpty(MultiLineRule, CommitMessageBodyRule):
    name = "body-first-line-empty"
    id = "B4"

    def validate(self, lines):
        if len(lines) >= 1:
            if lines[0] != "":
                return [RuleViolation(self.id, "Second line is not empty", lines[0], 2)]
