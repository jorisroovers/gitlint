from gitlint.tests.base import BaseTestCase
from gitlint import rules


class BodyRuleTests(BaseTestCase):
    def test_max_line_length(self):
        rule = rules.BodyMaxLineLength()

        # assert no error
        violation = rule.validate("a" * 80, None)
        self.assertIsNone(violation)

        # assert error on line length > 80
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (81>80)", "a" * 81)
        violations = rule.validate("a" * 81, None)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check no violation on length 73
        rule = rules.BodyMaxLineLength({'line-length': 120})
        violations = rule.validate("a" * 73, None)
        self.assertIsNone(violations)

        # assert raise on 121
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (121>120)", "a" * 121)
        violations = rule.validate("a" * 121, None)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_whitespace(self):
        rule = rules.BodyTrailingWhitespace()

        # assert no error
        violations = rule.validate("a", None)
        self.assertIsNone(violations)

        # trailing space
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", "a ")
        violations = rule.validate("a ", None)
        self.assertListEqual(violations, [expected_violation])

        # trailing tab
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", "a\t")
        violations = rule.validate("a\t", None)
        self.assertListEqual(violations, [expected_violation])

    def test_hard_tabs(self):
        rule = rules.BodyHardTab()

        # assert no error
        violations = rule.validate("This is a test", None)
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = rules.RuleViolation("B3", "Line contains hard tab characters (\\t)", "This is a\ttest")
        violations = rule.validate("This is a\ttest", None)
        self.assertListEqual(violations, [expected_violation])

    def test_body_first_line_empty(self):
        rule = rules.BodyFirstLineEmpty()

        # assert no error
        gitcontext = self.gitcontext("Title\n\nThis is the second body line")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = rules.RuleViolation("B4", "Second line is not empty", "not empty", 2)

        gitcontext = self.gitcontext("Title\nnot empty\nThis is the second body line")
        violations = rule.validate(gitcontext)
        self.assertListEqual(violations, [expected_violation])

    def test_body_min_length(self):
        rule = rules.BodyMinLength()

        # assert no error - body is long enough
        gitcontext = self.gitcontext("Title\n\nThis is the second body line\n")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert no error - no body
        gitcontext = self.gitcontext("Title\n")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert no error - short but more than one body line
        gitcontext = self.gitcontext("Title\n\nsecond\nthird\n")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # body is too short
        expected_violation = rules.RuleViolation("B5", "Body message is too short (8<20)", "tooshort", 3)

        gitcontext = self.gitcontext("Title\n\ntooshort\n")
        violations = rule.validate(gitcontext)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check violation on length 21
        expected_violation = rules.RuleViolation("B5", "Body message is too short (21<120)", "a" * 21, 3)

        rule = rules.BodyMinLength({'min-length': 120})
        gitcontext = self.gitcontext("Title\n\n%s\n" % ("a" * 21))
        violations = rule.validate(gitcontext)
        self.assertListEqual(violations, [expected_violation])

    def test_body_missing(self):
        rule = rules.BodyMissing()

        # assert no error - body is present
        gitcontext = self.gitcontext("Title\n\nThis is the first body line\n")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # body is too short
        expected_violation = rules.RuleViolation("B6", "Body message is missing", None, 3)

        gitcontext = self.gitcontext("Title\n")
        violations = rule.validate(gitcontext)
        self.assertListEqual(violations, [expected_violation])

    def test_body_missing_merge_commit(self):
        rule = rules.BodyMissing()

        # assert no error - merge commit
        gitcontext = self.gitcontext("Merge: Title\n")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert error for merge commits if ignore-merge-commits is disabled
        rule = rules.BodyMissing({'ignore-merge-commits': False})
        violations = rule.validate(gitcontext)
        expected_violation = rules.RuleViolation("B6", "Body message is missing", None, 3)
        self.assertListEqual(violations, [expected_violation])

    def test_body_changed_file_mention(self):
        rule = rules.BodyChangedFileMention()

        # assert no error when no files have changed and no files need to be mentioned
        gitcontext = self.gitcontext("This is a test\n\nHere is a mention of foo/test.py")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert no error when no files have changed but certain files need to be mentioned on change
        rule = rules.BodyChangedFileMention({'files': "bar.txt,foo/test.py"})
        gitcontext = self.gitcontext("This is a test\n\nHere is a mention of foo/test.py")
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert no error if a file has changed and is mentioned
        gitcontext = self.gitcontext("This is a test\n\nHere is a mention of foo/test.py", ["foo/test.py"])
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert no error if multiple files have changed and are mentioned
        commit_msg = "This is a test\n\nHere is a mention of foo/test.py\nAnd here is a mention of bar.txt"
        gitcontext = self.gitcontext(commit_msg, ["foo/test.py", "bar.txt"])
        violations = rule.validate(gitcontext)
        self.assertIsNone(violations)

        # assert error if file has changed and is not mentioned
        commit_msg = "This is a test\n\nHere is a mention of\nAnd here is a mention of bar.txt"
        gitcontext = self.gitcontext(commit_msg, ["foo/test.py", "bar.txt"])
        violations = rule.validate(gitcontext)
        expected_violation = rules.RuleViolation("B7", "Body does not mention changed file 'foo/test.py'", None, 4)
        self.assertEqual([expected_violation], violations)

        # assert multiple errors if  multiple files habe changed and are not mentioned
        commit_msg = "This is a test\n\nHere is a mention of\nAnd here is a mention of"
        gitcontext = self.gitcontext(commit_msg, ["foo/test.py", "bar.txt"])
        violations = rule.validate(gitcontext)
        expected_violation_2 = rules.RuleViolation("B7", "Body does not mention changed file 'bar.txt'", None, 4)
        self.assertEqual([expected_violation_2, expected_violation], violations)
