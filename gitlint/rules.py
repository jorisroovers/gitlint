from abc import abstractmethod, ABCMeta
from gitlint.options import IntOption, BoolOption, StrOption, ListOption

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
            if actual_option is not None:
                self.options[op_spec.name].set(actual_option)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name

    def __str__(self):
        return "{} {}".format(self.id, self.name)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover

    @abstractmethod
    def validate(self):
        pass  # pragma: no cover


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
        return "{}: {} {}: \"{}\"".format(self.line_nr, self.rule_id, self.message, self.content)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class MaxLineLength(LineRule):
    name = "max-line-length"
    id = "R1"
    options_spec = [IntOption('line-length', 80, "Max line length")]
    violation_message = "Line exceeds max length ({0}>{1})"

    def validate(self, line, gitcontext):
        max_length = self.options['line-length'].value
        if len(line) > max_length:
            return [RuleViolation(self.id, self.violation_message.format(len(line), max_length), line)]


class TrailingWhiteSpace(LineRule):
    name = "trailing-whitespace"
    id = "R2"
    violation_message = "Line has trailing whitespace"

    def validate(self, line, gitcontext):
        pattern = re.compile(r"\s$")
        if pattern.search(line):
            return [RuleViolation(self.id, self.violation_message, line)]


class HardTab(LineRule):
    name = "hard-tab"
    id = "R3"
    violation_message = "Line contains hard tab characters (\\t)"

    def validate(self, line, gitcontext):
        if "\t" in line:
            return [RuleViolation(self.id, self.violation_message, line)]


class LineMustNotContainWord(LineRule):
    """ Violation if a line contains one of a list of words (NOTE: using a word in the list inside another word is not a
    violation, e.g: WIPING is not a violation if 'WIP' is a word that is not allowed.) """
    name = "line-must-not-contain"
    id = "R5"
    options_spec = [ListOption('words', [], "Comma separated list of words that should not be found")]
    violation_message = "Line contains {0}"

    def validate(self, line, gitcontext):
        strings = self.options['words'].value
        violations = []
        for string in strings:
            regex = re.compile(r"\b%s\b" % string.lower(), re.I)
            match = regex.search(line.lower())
            if match:
                violations.append(RuleViolation(self.id, self.violation_message.format(string), line))
        return violations if violations else None


class LeadingWhiteSpace(LineRule):
    name = "leading-whitespace"
    id = "R6"
    violation_message = "Line has leading whitespace"

    def validate(self, line, gitcontext):
        pattern = re.compile(r"^\s")
        if pattern.search(line):
            return [RuleViolation(self.id, self.violation_message, line)]


class TitleMaxLength(MaxLineLength, CommitMessageTitleRule):
    name = "title-max-length"
    id = "T1"
    options_spec = [IntOption('line-length', 72, "Max line length")]
    violation_message = "Title exceeds max length ({0}>{1})"


class TitleTrailingWhitespace(TrailingWhiteSpace, CommitMessageTitleRule):
    name = "title-trailing-whitespace"
    id = "T2"
    violation_message = "Title has trailing whitespace"


class TitleTrailingPunctuation(CommitMessageTitleRule):
    name = "title-trailing-punctuation"
    id = "T3"

    def validate(self, line, gitcontext):
        punctuation_marks = '?:!.,;'
        for punctuation_mark in punctuation_marks:
            if gitcontext.commit_msg.title.endswith(punctuation_mark):
                return [RuleViolation(self.id, "Title has trailing punctuation ({0})".format(punctuation_mark),
                                      gitcontext.commit_msg.title)]


class TitleHardTab(HardTab, CommitMessageTitleRule):
    name = "title-hard-tab"
    id = "T4"
    violation_message = "Title contains hard tab characters (\\t)"


class TitleMustNotContainWord(LineMustNotContainWord, CommitMessageTitleRule):
    name = "title-must-not-contain-word"
    id = "T5"
    options_spec = [ListOption('words', ['WIP'], "Must not contain word")]
    violation_message = "Title contains the word '{0}' (case-insensitive)"


class TitleLeadingWhitespace(LeadingWhiteSpace, CommitMessageTitleRule):
    name = "title-leading-whitespace"
    id = "T6"
    violation_message = "Title has leading whitespace"


class TitleRegexMatches(CommitMessageTitleRule):
    name = "title-match-regex"
    id = "T7"
    options_spec = [StrOption('regex', ".*", "Regex the title should match")]

    def validate(self, line, gitcontext):
        regex = self.options['regex'].value
        pattern = re.compile(regex)
        if not pattern.search(gitcontext.commit_msg.title):
            violation_msg = "Title does match regex ({})".format(regex)
            return [RuleViolation(self.id, violation_msg, gitcontext.commit_msg.title)]


class BodyMaxLineLength(MaxLineLength, CommitMessageBodyRule):
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

    def validate(self, gitcontext):
        if len(gitcontext.commit_msg.body) >= 1:
            first_line = gitcontext.commit_msg.body[0]
            if first_line != "":
                return [RuleViolation(self.id, "Second line is not empty", first_line, 2)]


class BodyMinLength(MultiLineRule, CommitMessageBodyRule):
    name = "body-min-length"
    id = "B5"
    options_spec = [IntOption('min-length', 20, "Minimum body length")]

    def validate(self, gitcontext):
        min_length = self.options['min-length'].value
        lines = gitcontext.commit_msg.body
        if len(lines) == 3:
            actual_length = len(lines[1])
            if lines[0] == "" and actual_length <= min_length:
                violation_message = "Body message is too short ({}<{})".format(actual_length, min_length)
                return [RuleViolation(self.id, violation_message, lines[1], 3)]


class BodyMissing(MultiLineRule, CommitMessageBodyRule):
    name = "body-is-missing"
    id = "B6"
    options_spec = [BoolOption('ignore-merge-commits', True, "Ignore merge commits")]

    def validate(self, gitcontext):
        # ignore merges when option tells us to, which may have no body
        if self.options['ignore-merge-commits'].value and gitcontext.commit_msg.title.startswith("Merge"):
            return
        if len(gitcontext.commit_msg.body) <= 2:
            return [RuleViolation(self.id, "Body message is missing", None, 3)]


class BodyChangedFileMention(MultiLineRule, CommitMessageBodyRule):
    name = "body-changed-file-mention"
    id = "B7"
    options_spec = [ListOption('files', [], "Files that need to be mentioned ")]

    def validate(self, gitcontext):
        violations = []
        for needs_mentioned_file in self.options['files'].value:
            # if a file that we need to look out for is actually changed, then check whether it occurs
            # in the commit msg body
            if needs_mentioned_file in gitcontext.changed_files:
                if needs_mentioned_file not in " ".join(gitcontext.commit_msg.body):
                    violation_message = "Body does not mention changed file '{}'".format(needs_mentioned_file)
                    violations.append(RuleViolation(self.id, violation_message, None,
                                                    len(gitcontext.commit_msg.body) + 1))
        return violations if violations else None
