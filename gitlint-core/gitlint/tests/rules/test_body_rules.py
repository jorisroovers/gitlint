# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint import rules


class BodyRuleTests(BaseTestCase):
    def test_max_line_length(self):
        rule = rules.BodyMaxLineLength()

        # assert no error
        violation = rule.validate("å" * 80, None)
        self.assertIsNone(violation)

        # assert error on line length > 80
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (81>80)", "å" * 81)
        violations = rule.validate("å" * 81, None)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check no violation on length 73
        rule = rules.BodyMaxLineLength({'line-length': 120})
        violations = rule.validate("å" * 73, None)
        self.assertIsNone(violations)

        # assert raise on 121
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (121>120)", "å" * 121)
        violations = rule.validate("å" * 121, None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_whitespace(self):
        rule = rules.BodyTrailingWhitespace()

        # assert no error
        violations = rule.validate("å", None)
        self.assertIsNone(violations)

        # trailing space
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", "å ")
        violations = rule.validate("å ", None)
        self.assertListEqual(violations, [expected_violation])

        # trailing tab
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", "å\t")
        violations = rule.validate("å\t", None)
        self.assertListEqual(violations, [expected_violation])

    def test_hard_tabs(self):
        rule = rules.BodyHardTab()

        # assert no error
        violations = rule.validate("This is ã test", None)
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = rules.RuleViolation("B3", "Line contains hard tab characters (\\t)", "This is å\ttest")
        violations = rule.validate("This is å\ttest", None)
        self.assertListEqual(violations, [expected_violation])

    def test_body_first_line_empty(self):
        rule = rules.BodyFirstLineEmpty()

        # assert no error
        commit = self.gitcommit("Tïtle\n\nThis is the secōnd body line")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # second line not empty
        expected_violation = rules.RuleViolation("B4", "Second line is not empty", "nöt empty", 2)

        commit = self.gitcommit("Tïtle\nnöt empty\nThis is the secönd body line")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

    def test_body_min_length(self):
        rule = rules.BodyMinLength()

        # assert no error - body is long enough
        commit = self.gitcommit("Title\n\nThis is the second body line\n")

        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error - no body
        commit = self.gitcommit("Tïtle\n")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # body is too short
        expected_violation = rules.RuleViolation("B5", "Body message is too short (8<20)", "töoshort", 3)

        commit = self.gitcommit("Tïtle\n\ntöoshort\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

        # assert error - short across multiple lines
        expected_violation = rules.RuleViolation("B5", "Body message is too short (11<20)", "secöndthïrd", 3)
        commit = self.gitcommit("Tïtle\n\nsecönd\nthïrd\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check violation on length 21
        expected_violation = rules.RuleViolation("B5", "Body message is too short (21<120)", "å" * 21, 3)

        rule = rules.BodyMinLength({'min-length': 120})
        commit = self.gitcommit("Title\n\n{0}\n".format("å" * 21))  # pylint: disable=consider-using-f-string
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

        # Make sure we don't get the error if the body-length is exactly the min-length
        rule = rules.BodyMinLength({'min-length': 8})
        commit = self.gitcommit("Tïtle\n\n{0}\n".format("å" * 8))  # pylint: disable=consider-using-f-string
        violations = rule.validate(commit)
        self.assertIsNone(violations)

    def test_body_missing(self):
        rule = rules.BodyMissing()

        # assert no error - body is present
        commit = self.gitcommit("Tïtle\n\nThis ïs the first body line\n")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # body is too short
        expected_violation = rules.RuleViolation("B6", "Body message is missing", None, 3)

        commit = self.gitcommit("Tïtle\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

    def test_body_missing_multiple_empty_new_lines(self):
        rule = rules.BodyMissing()

        # body is too short
        expected_violation = rules.RuleViolation("B6", "Body message is missing", None, 3)

        commit = self.gitcommit("Tïtle\n\n\n\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

    def test_body_missing_merge_commit(self):
        rule = rules.BodyMissing()

        # assert no error - merge commit
        commit = self.gitcommit("Merge: Tïtle\n")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert error for merge commits if ignore-merge-commits is disabled
        rule = rules.BodyMissing({'ignore-merge-commits': False})
        violations = rule.validate(commit)
        expected_violation = rules.RuleViolation("B6", "Body message is missing", None, 3)
        self.assertListEqual(violations, [expected_violation])

    def test_body_changed_file_mention(self):
        rule = rules.BodyChangedFileMention()

        # assert no error when no files have changed and no files need to be mentioned
        commit = self.gitcommit("This is a test\n\nHere is a mention of föo/test.py")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error when no files have changed but certain files need to be mentioned on change
        rule = rules.BodyChangedFileMention({'files': "bar.txt,föo/test.py"})
        commit = self.gitcommit("This is a test\n\nHere is a mention of föo/test.py")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error if a file has changed and is mentioned
        commit = self.gitcommit("This is a test\n\nHere is a mention of föo/test.py", ["föo/test.py"])
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error if multiple files have changed and are mentioned
        commit_msg = "This is a test\n\nHere is a mention of föo/test.py\nAnd here is a mention of bar.txt"
        commit = self.gitcommit(commit_msg, ["föo/test.py", "bar.txt"])
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert error if file has changed and is not mentioned
        commit_msg = "This is a test\n\nHere is å mention of\nAnd here is a mention of bar.txt"
        commit = self.gitcommit(commit_msg, ["föo/test.py", "bar.txt"])
        violations = rule.validate(commit)
        expected_violation = rules.RuleViolation("B7", "Body does not mention changed file 'föo/test.py'", None, 4)
        self.assertEqual([expected_violation], violations)

        # assert multiple errors if multiple files have changed and are not mentioned
        commit_msg = "This is å test\n\nHere is a mention of\nAnd here is a mention of"
        commit = self.gitcommit(commit_msg, ["föo/test.py", "bar.txt"])
        violations = rule.validate(commit)
        expected_violation_2 = rules.RuleViolation("B7", "Body does not mention changed file 'bar.txt'", None, 4)
        self.assertEqual([expected_violation_2, expected_violation], violations)

    def test_body_match_regex(self):
        # We intentionally add 2 newlines at the end of our commit message as that's how git will pass the
        # message. This way we also test that the rule strips off the last line.
        commit = self.gitcommit("US1234: åbc\nIgnored\nBödy\nFöo\nMy-Commit-Tag: föo\n\n")

        # assert no violation on default regex (=everything allowed)
        rule = rules.BodyRegexMatches()
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no violation on matching regex
        # (also note that first body line - in between title and rest of body - is ignored)
        rule = rules.BodyRegexMatches({'regex': "^Bödy(.*)"})
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert we can do end matching (and last empty line is ignored)
        # (also note that first body line - in between title and rest of body - is ignored)
        rule = rules.BodyRegexMatches({'regex': "My-Commit-Tag: föo$"})
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # common use-case: matching that a given line is present
        rule = rules.BodyRegexMatches({'regex': "(.*)Föo(.*)"})
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert violation on non-matching body
        rule = rules.BodyRegexMatches({'regex': "^Tëst(.*)Foo"})
        violations = rule.validate(commit)
        expected_violation = rules.RuleViolation("B8", "Body does not match regex (^Tëst(.*)Foo)", None, 6)
        self.assertListEqual(violations, [expected_violation])

        # assert no violation on None regex
        rule = rules.BodyRegexMatches({'regex': None})
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # Assert no issues when there's no body or a weird body variation
        bodies = ["åbc", "åbc\n", "åbc\nföo\n", "åbc\n\n", "åbc\nföo\nblå", "åbc\nföo\nblå\n"]
        for body in bodies:
            commit = self.gitcommit(body)
            rule = rules.BodyRegexMatches({'regex': ".*"})
            violations = rule.validate(commit)
            self.assertIsNone(violations)
