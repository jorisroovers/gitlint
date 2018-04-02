# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import TitleMaxLength, TitleTrailingWhitespace, TitleHardTab, TitleMustNotContainWord, \
    TitleTrailingPunctuation, TitleLeadingWhitespace, TitleRegexMatches, RuleViolation


class TitleRuleTests(BaseTestCase):
    def test_max_line_length(self):
        rule = TitleMaxLength()

        # assert no error
        violation = rule.validate(u"å" * 72, None)
        self.assertIsNone(violation)

        # assert error on line length > 72
        expected_violation = RuleViolation("T1", "Title exceeds max length (73>72)", u"å" * 73)
        violations = rule.validate(u"å" * 73, None)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check no violation on length 73
        rule = TitleMaxLength({'line-length': 120})
        violations = rule.validate(u"å" * 73, None)
        self.assertIsNone(violations)

        # assert raise on 121
        expected_violation = RuleViolation("T1", "Title exceeds max length (121>120)", u"å" * 121)
        violations = rule.validate(u"å" * 121, None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_whitespace(self):
        rule = TitleTrailingWhitespace()

        # assert no error
        violations = rule.validate(u"å", None)
        self.assertIsNone(violations)

        # trailing space
        expected_violation = RuleViolation("T2", "Title has trailing whitespace", u"å ")
        violations = rule.validate(u"å ", None)
        self.assertListEqual(violations, [expected_violation])

        # trailing tab
        expected_violation = RuleViolation("T2", "Title has trailing whitespace", u"å\t")
        violations = rule.validate(u"å\t", None)
        self.assertListEqual(violations, [expected_violation])

    def test_hard_tabs(self):
        rule = TitleHardTab()

        # assert no error
        violations = rule.validate(u"This is å test", None)
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = RuleViolation("T4", "Title contains hard tab characters (\\t)", u"This is å\ttest")
        violations = rule.validate(u"This is å\ttest", None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_punctuation(self):
        rule = TitleTrailingPunctuation()

        # assert no error
        violations = rule.validate(u"This is å test", None)
        self.assertIsNone(violations)

        # assert errors for different punctuations
        punctuation = u"?:!.,;"
        for char in punctuation:
            line = u"This is å test" + char  # note that make sure to include some unicode!
            gitcontext = self.gitcontext(line)
            expected_violation = RuleViolation("T3", u"Title has trailing punctuation ({0})".format(char), line)
            violations = rule.validate(line, gitcontext)
            self.assertListEqual(violations, [expected_violation])

    def test_title_must_not_contain_word(self):
        rule = TitleMustNotContainWord()

        # no violations
        violations = rule.validate(u"This is å test", None)
        self.assertIsNone(violations)

        # no violation if WIP occurs inside a wor
        violations = rule.validate(u"This is å wiping test", None)
        self.assertIsNone(violations)

        # match literally
        violations = rule.validate(u"WIP This is å test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                           u"WIP This is å test")
        self.assertListEqual(violations, [expected_violation])

        # match case insensitive
        violations = rule.validate(u"wip This is å test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                           u"wip This is å test")
        self.assertListEqual(violations, [expected_violation])

        # match if there is a colon after the word
        violations = rule.validate(u"WIP:This is å test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                           u"WIP:This is å test")
        self.assertListEqual(violations, [expected_violation])

        # match multiple words
        rule = TitleMustNotContainWord({'words': u"wip,test,å"})
        violations = rule.validate(u"WIP:This is å test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'wip' (case-insensitive)",
                                           u"WIP:This is å test")
        expected_violation2 = RuleViolation("T5", "Title contains the word 'test' (case-insensitive)",
                                            u"WIP:This is å test")
        expected_violation3 = RuleViolation("T5", u"Title contains the word 'å' (case-insensitive)",
                                            u"WIP:This is å test")
        self.assertListEqual(violations, [expected_violation, expected_violation2, expected_violation3])

    def test_leading_whitespace(self):
        rule = TitleLeadingWhitespace()

        # assert no error
        violations = rule.validate("a", None)
        self.assertIsNone(violations)

        # leading space
        expected_violation = RuleViolation("T6", "Title has leading whitespace", " a")
        violations = rule.validate(" a", None)
        self.assertListEqual(violations, [expected_violation])

        # leading tab
        expected_violation = RuleViolation("T6", "Title has leading whitespace", "\ta")
        violations = rule.validate("\ta", None)
        self.assertListEqual(violations, [expected_violation])

        # unicode test
        expected_violation = RuleViolation("T6", "Title has leading whitespace", u" ☺")
        violations = rule.validate(u" ☺", None)
        self.assertListEqual(violations, [expected_violation])

    def test_regex_matches(self):
        commit = self.gitcommit(u"US1234: åbc\n")

        # assert no violation on default regex (=everything allowed)
        rule = TitleRegexMatches()
        violations = rule.validate(commit.message.title, commit)
        self.assertIsNone(violations)

        # assert no violation on matching regex
        rule = TitleRegexMatches({'regex': u"^US[0-9]*: å"})
        violations = rule.validate(commit.message.title, commit)
        self.assertIsNone(violations)

        # assert violation when no matching regex
        rule = TitleRegexMatches({'regex': u"^UÅ[0-9]*"})
        violations = rule.validate(commit.message.title, commit)
        expected_violation = RuleViolation("T7", u"Title does not match regex (^UÅ[0-9]*)", u"US1234: åbc")
        self.assertListEqual(violations, [expected_violation])
