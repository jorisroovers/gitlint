from gitlint.tests.base import BaseTestCase
from gitlint.rules import TitleMaxLength, TitleTrailingWhitespace, TitleHardTab, TitleMustNotContainWord, \
    TitleTrailingPunctuation, TitleLeadingWhitespace, TitleRegexMatches, RuleViolation


class TitleRuleTests(BaseTestCase):
    def test_max_line_length(self):
        rule = TitleMaxLength()

        # assert no error
        violation = rule.validate("a" * 72, None)
        self.assertIsNone(violation)

        # assert error on line length > 72
        expected_violation = RuleViolation("T1", "Title exceeds max length (73>72)", "a" * 73)
        violations = rule.validate("a" * 73, None)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check no violation on length 73
        rule = TitleMaxLength({'line-length': 120})
        violations = rule.validate("a" * 73, None)
        self.assertIsNone(violations)

        # assert raise on 121
        expected_violation = RuleViolation("T1", "Title exceeds max length (121>120)", "a" * 121)
        violations = rule.validate("a" * 121, None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_whitespace(self):
        rule = TitleTrailingWhitespace()

        # assert no error
        violations = rule.validate("a", None)
        self.assertIsNone(violations)

        # trailing space
        expected_violation = RuleViolation("T2", "Title has trailing whitespace", "a ")
        violations = rule.validate("a ", None)
        self.assertListEqual(violations, [expected_violation])

        # trailing tab
        expected_violation = RuleViolation("T2", "Title has trailing whitespace", "a\t")
        violations = rule.validate("a\t", None)
        self.assertListEqual(violations, [expected_violation])

    def test_hard_tabs(self):
        rule = TitleHardTab()

        # assert no error
        violations = rule.validate("This is a test", None)
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = RuleViolation("T4", "Title contains hard tab characters (\\t)", "This is a\ttest")
        violations = rule.validate("This is a\ttest", None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_punctuation(self):
        rule = TitleTrailingPunctuation()

        # assert no error
        violations = rule.validate(None, self.gitcontext("This is a test"))
        self.assertIsNone(violations)

        # assert errors for different punctuations
        punctuation = "?:!.,;"
        for char in punctuation:
            line = "This is a test" + char
            gitcontext = self.gitcontext(line)
            expected_violation = RuleViolation("T3", "Title has trailing punctuation ({})".format(char), line)
            violations = rule.validate(None, gitcontext)
            self.assertListEqual(violations, [expected_violation])

    def test_title_must_not_contain_word(self):
        rule = TitleMustNotContainWord()

        # no violations
        violations = rule.validate("This is a test", None)
        self.assertIsNone(violations)

        # no violation if WIP occurs inside a wor
        violations = rule.validate("This is a wiping test", None)
        self.assertIsNone(violations)

        # match literally
        violations = rule.validate("WIP This is a test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                           "WIP This is a test")
        self.assertListEqual(violations, [expected_violation])

        # match case insensitive
        violations = rule.validate("wip This is a test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                           "wip This is a test")
        self.assertListEqual(violations, [expected_violation])

        # match if there is a colon after the word
        violations = rule.validate("WIP:This is a test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                           "WIP:This is a test")
        self.assertListEqual(violations, [expected_violation])

        # match multiple words
        rule = TitleMustNotContainWord({'words': "wip,test"})
        violations = rule.validate("WIP:This is a test", None)
        expected_violation = RuleViolation("T5", "Title contains the word 'wip' (case-insensitive)",
                                           "WIP:This is a test")
        expected_violation2 = RuleViolation("T5", "Title contains the word 'test' (case-insensitive)",
                                            "WIP:This is a test")
        self.assertListEqual(violations, [expected_violation, expected_violation2])

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

    def test_match_regex(self):
        gitcontext = self.gitcontext("US1234: abc\n")

        # assert no violation on default regex (=everything allowed)
        rule = TitleRegexMatches()
        violations = rule.validate(None, gitcontext)
        self.assertIsNone(violations)

        # assert no violation on matching regex
        rule = TitleRegexMatches({'regex': "^US[0-9]*"})
        violations = rule.validate(None, gitcontext)
        self.assertIsNone(violations)

        # assert violation when no matching regex
        rule = TitleRegexMatches({'regex': "^UA[0-9]*"})
        violations = rule.validate(None, gitcontext)
        expected_violation = RuleViolation("T7", "Title does match regex (^UA[0-9]*)", "US1234: abc")
        self.assertListEqual(violations, [expected_violation])
