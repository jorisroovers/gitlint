import copy
import re

from gitlint.options import IntOption, BoolOption, StrOption, ListOption
from gitlint.utils import sstr


class Rule(object):
    """ Class representing gitlint rules. """
    options_spec = []
    id = None
    name = None
    target = None

    def __init__(self, opts=None):
        if not opts:
            opts = {}
        self.options = {}
        for op_spec in self.options_spec:
            self.options[op_spec.name] = copy.deepcopy(op_spec)
            actual_option = opts.get(op_spec.name)
            if actual_option is not None:
                self.options[op_spec.name].set(actual_option)

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and \
               self.options == other.options and self.target == other.target  # noqa

    def __str__(self):
        return sstr(self)  # pragma: no cover

    def __unicode__(self):
        return u"{0} {1}".format(self.id, self.name)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class CommitRule(Rule):
    """ Class representing rules that act on an entire commit at once """
    pass


class LineRule(Rule):
    """ Class representing rules that act on a line by line basis """
    pass


class LineRuleTarget(object):
    """ Base class for LineRule targets. A LineRuleTarget specifies where a given rule will be applied
    (e.g. commit message title, commit message body).
    Each LineRule MUST have a target specified. """
    pass


class CommitMessageTitle(LineRuleTarget):
    """ Target class used for rules that apply to a commit message title """
    pass


class CommitMessageBody(LineRuleTarget):
    """ Target class used for rules that apply to a commit message body """
    pass


class RuleViolation(object):
    """ Class representing a violation of a rule. I.e.: When a rule is broken, the rule will instantiate this class
    to indicate how and where the rule was broken. """

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
        return sstr(self)  # pragma: no cover

    def __unicode__(self):
        return u"{0}: {1} {2}: \"{3}\"".format(self.line_nr, self.rule_id, self.message,
                                               self.content)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class MaxLineLength(LineRule):
    name = "max-line-length"
    id = "R1"
    options_spec = [IntOption('line-length', 80, "Max line length")]
    violation_message = "Line exceeds max length ({0}>{1})"

    def validate(self, line, _commit):
        max_length = self.options['line-length'].value
        if len(line) > max_length:
            return [RuleViolation(self.id, self.violation_message.format(len(line), max_length), line)]


class TrailingWhiteSpace(LineRule):
    name = "trailing-whitespace"
    id = "R2"
    violation_message = "Line has trailing whitespace"

    def validate(self, line, _commit):
        pattern = re.compile(r"\s$", re.UNICODE)
        if pattern.search(line):
            return [RuleViolation(self.id, self.violation_message, line)]


class HardTab(LineRule):
    name = "hard-tab"
    id = "R3"
    violation_message = "Line contains hard tab characters (\\t)"

    def validate(self, line, _commit):
        if "\t" in line:
            return [RuleViolation(self.id, self.violation_message, line)]


class LineMustNotContainWord(LineRule):
    """ Violation if a line contains one of a list of words (NOTE: using a word in the list inside another word is not
    a violation, e.g: WIPING is not a violation if 'WIP' is a word that is not allowed.) """
    name = "line-must-not-contain"
    id = "R5"
    options_spec = [ListOption('words', [], "Comma separated list of words that should not be found")]
    violation_message = u"Line contains {0}"

    def validate(self, line, _commit):
        strings = self.options['words'].value
        violations = []
        for string in strings:
            regex = re.compile(r"\b%s\b" % string.lower(), re.IGNORECASE | re.UNICODE)
            match = regex.search(line.lower())
            if match:
                violations.append(RuleViolation(self.id, self.violation_message.format(string), line))
        return violations if violations else None


class LeadingWhiteSpace(LineRule):
    name = "leading-whitespace"
    id = "R6"
    violation_message = "Line has leading whitespace"

    def validate(self, line, _commit):
        pattern = re.compile(r"^\s", re.UNICODE)
        if pattern.search(line):
            return [RuleViolation(self.id, self.violation_message, line)]


class TitleMaxLength(MaxLineLength):
    name = "title-max-length"
    id = "T1"
    target = CommitMessageTitle
    options_spec = [IntOption('line-length', 72, "Max line length")]
    violation_message = "Title exceeds max length ({0}>{1})"


class TitleTrailingWhitespace(TrailingWhiteSpace):
    name = "title-trailing-whitespace"
    id = "T2"
    target = CommitMessageTitle
    violation_message = "Title has trailing whitespace"


class TitleTrailingPunctuation(LineRule):
    name = "title-trailing-punctuation"
    id = "T3"
    target = CommitMessageTitle

    def validate(self, title, _commit):
        punctuation_marks = '?:!.,;'
        for punctuation_mark in punctuation_marks:
            if title.endswith(punctuation_mark):
                return [RuleViolation(self.id, u"Title has trailing punctuation ({0})".format(punctuation_mark), title)]


class TitleHardTab(HardTab):
    name = "title-hard-tab"
    id = "T4"
    target = CommitMessageTitle
    violation_message = "Title contains hard tab characters (\\t)"


class TitleMustNotContainWord(LineMustNotContainWord):
    name = "title-must-not-contain-word"
    id = "T5"
    target = CommitMessageTitle
    options_spec = [ListOption('words', ["WIP"], "Must not contain word")]
    violation_message = u"Title contains the word '{0}' (case-insensitive)"


class TitleLeadingWhitespace(LeadingWhiteSpace):
    name = "title-leading-whitespace"
    id = "T6"
    target = CommitMessageTitle
    violation_message = "Title has leading whitespace"


class TitleRegexMatches(LineRule):
    name = "title-match-regex"
    id = "T7"
    target = CommitMessageTitle
    options_spec = [StrOption('regex', ".*", "Regex the title should match")]

    def validate(self, title, _commit):
        regex = self.options['regex'].value
        pattern = re.compile(regex, re.UNICODE)
        if not pattern.search(title):
            violation_msg = u"Title does not match regex ({0})".format(regex)
            return [RuleViolation(self.id, violation_msg, title)]


class BodyMaxLineLength(MaxLineLength):
    name = "body-max-line-length"
    id = "B1"
    target = CommitMessageBody


class BodyTrailingWhitespace(TrailingWhiteSpace):
    name = "body-trailing-whitespace"
    id = "B2"
    target = CommitMessageBody


class BodyHardTab(HardTab):
    name = "body-hard-tab"
    id = "B3"
    target = CommitMessageBody


class BodyFirstLineEmpty(CommitRule):
    name = "body-first-line-empty"
    id = "B4"

    def validate(self, commit):
        if len(commit.message.body) >= 1:
            first_line = commit.message.body[0]
            if first_line != "":
                return [RuleViolation(self.id, "Second line is not empty", first_line, 2)]


class BodyMinLength(CommitRule):
    name = "body-min-length"
    id = "B5"
    options_spec = [IntOption('min-length', 20, "Minimum body length")]

    def validate(self, commit):
        min_length = self.options['min-length'].value
        body_message_no_newline = "".join([line for line in commit.message.body if line is not None])
        actual_length = len(body_message_no_newline)
        if actual_length > 0 and actual_length < min_length:
            violation_message = "Body message is too short ({0}<{1})".format(actual_length, min_length)
            return [RuleViolation(self.id, violation_message, body_message_no_newline, 3)]


class BodyMissing(CommitRule):
    name = "body-is-missing"
    id = "B6"
    options_spec = [BoolOption('ignore-merge-commits', True, "Ignore merge commits")]

    def validate(self, commit):
        # ignore merges when option tells us to, which may have no body
        if self.options['ignore-merge-commits'].value and commit.is_merge_commit:
            return
        if len(commit.message.body) < 2:
            return [RuleViolation(self.id, "Body message is missing", None, 3)]


class BodyChangedFileMention(CommitRule):
    name = "body-changed-file-mention"
    id = "B7"
    options_spec = [ListOption('files', [], "Files that need to be mentioned")]

    def validate(self, commit):
        violations = []
        for needs_mentioned_file in self.options['files'].value:
            # if a file that we need to look out for is actually changed, then check whether it occurs
            # in the commit msg body
            if needs_mentioned_file in commit.changed_files:
                if needs_mentioned_file not in " ".join(commit.message.body):
                    violation_message = u"Body does not mention changed file '{0}'".format(needs_mentioned_file)
                    violations.append(RuleViolation(self.id, violation_message, None, len(commit.message.body) + 1))
        return violations if violations else None
