# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint import rules


class BodyRuleTests(BaseTestCase):
    def test_max_line_length(self):
        rule = rules.BodyMaxLineLength()

        # assert no error
        violation = rule.validate(u"å" * 80, None)
        self.assertIsNone(violation)

        # assert error on line length > 80
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (81>80)", u"å" * 81)
        violations = rule.validate(u"å" * 81, None)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check no violation on length 73
        rule = rules.BodyMaxLineLength({'line-length': 120})
        violations = rule.validate(u"å" * 73, None)
        self.assertIsNone(violations)

        # assert raise on 121
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (121>120)", u"å" * 121)
        violations = rule.validate(u"å" * 121, None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_whitespace(self):
        rule = rules.BodyTrailingWhitespace()

        # assert no error
        violations = rule.validate(u"å", None)
        self.assertIsNone(violations)

        # trailing space
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", u"å ")
        violations = rule.validate(u"å ", None)
        self.assertListEqual(violations, [expected_violation])

        # trailing tab
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", u"å\t")
        violations = rule.validate(u"å\t", None)
        self.assertListEqual(violations, [expected_violation])

    def test_hard_tabs(self):
        rule = rules.BodyHardTab()

        # assert no error
        violations = rule.validate(u"This is ã test", None)
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = rules.RuleViolation("B3", "Line contains hard tab characters (\\t)", u"This is å\ttest")
        violations = rule.validate(u"This is å\ttest", None)
        self.assertListEqual(violations, [expected_violation])

    def test_body_first_line_empty(self):
        rule = rules.BodyFirstLineEmpty()

        # assert no error
        commit = self.gitcommit(u"Tïtle\n\nThis is the secōnd body line")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # second line not empty
        expected_violation = rules.RuleViolation("B4", "Second line is not empty", u"nöt empty", 2)

        commit = self.gitcommit(u"Tïtle\nnöt empty\nThis is the secönd body line")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

    def test_body_min_length(self):
        rule = rules.BodyMinLength()

        # assert no error - body is long enough
        commit = self.gitcommit("Title\n\nThis is the second body line\n")

        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error - no body
        commit = self.gitcommit(u"Tïtle\n")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # body is too short
        expected_violation = rules.RuleViolation("B5", "Body message is too short (8<20)", u"töoshort", 3)

        commit = self.gitcommit(u"Tïtle\n\ntöoshort\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

        # assert error - short across multiple lines
        expected_violation = rules.RuleViolation("B5", "Body message is too short (11<20)", u"secöndthïrd", 3)
        commit = self.gitcommit(u"Tïtle\n\nsecönd\nthïrd\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check violation on length 21
        expected_violation = rules.RuleViolation("B5", "Body message is too short (21<120)", u"å" * 21, 3)

        rule = rules.BodyMinLength({'min-length': 120})
        commit = self.gitcommit(u"Title\n\n%s\n" % (u"å" * 21))
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

        # Make sure we don't get the error if the body-length is exactly the min-length
        rule = rules.BodyMinLength({'min-length': 8})
        commit = self.gitcommit(u"Tïtle\n\n%s\n" % (u"å" * 8))
        violations = rule.validate(commit)
        self.assertIsNone(violations)

    def test_body_missing(self):
        rule = rules.BodyMissing()

        # assert no error - body is present
        commit = self.gitcommit(u"Tïtle\n\nThis ïs the first body line\n")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # body is too short
        expected_violation = rules.RuleViolation("B6", "Body message is missing", None, 3)

        commit = self.gitcommit(u"Tïtle\n")
        violations = rule.validate(commit)
        self.assertListEqual(violations, [expected_violation])

    def test_body_missing_merge_commit(self):
        rule = rules.BodyMissing()

        # assert no error - merge commit
        commit = self.gitcommit(u"Merge: Tïtle\n")
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
        commit = self.gitcommit(u"This is a test\n\nHere is a mention of föo/test.py")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error when no files have changed but certain files need to be mentioned on change
        rule = rules.BodyChangedFileMention({'files': u"bar.txt,föo/test.py"})
        commit = self.gitcommit(u"This is a test\n\nHere is a mention of föo/test.py")
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error if a file has changed and is mentioned
        commit = self.gitcommit(u"This is a test\n\nHere is a mention of föo/test.py", [u"föo/test.py"])
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert no error if multiple files have changed and are mentioned
        commit_msg = u"This is a test\n\nHere is a mention of föo/test.py\nAnd here is a mention of bar.txt"
        commit = self.gitcommit(commit_msg, [u"föo/test.py", "bar.txt"])
        violations = rule.validate(commit)
        self.assertIsNone(violations)

        # assert error if file has changed and is not mentioned
        commit_msg = u"This is a test\n\nHere is å mention of\nAnd here is a mention of bar.txt"
        commit = self.gitcommit(commit_msg, [u"föo/test.py", "bar.txt"])
        violations = rule.validate(commit)
        expected_violation = rules.RuleViolation("B7", u"Body does not mention changed file 'föo/test.py'", None, 4)
        self.assertEqual([expected_violation], violations)

        # assert multiple errors if  multiple files habe changed and are not mentioned
        commit_msg = u"This is å test\n\nHere is a mention of\nAnd here is a mention of"
        commit = self.gitcommit(commit_msg, [u"föo/test.py", "bar.txt"])
        violations = rule.validate(commit)
        expected_violation_2 = rules.RuleViolation("B7", "Body does not mention changed file 'bar.txt'", None, 4)
        self.assertEqual([expected_violation_2, expected_violation], violations)
