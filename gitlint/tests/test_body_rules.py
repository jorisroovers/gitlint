from gitlint.tests.base import BaseTestCase
from gitlint import rules


class BodyRuleTests(BaseTestCase):
    def test_max_line_length(self):
        rule = rules.BodyMaxLineLength()

        # assert no error
        violation = rule.validate("a" * 80)
        self.assertIsNone(violation)

        # assert error on line length > 80
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (81>80)", "a" * 81)
        violations = rule.validate("a" * 81)
        self.assertListEqual(violations, [expected_violation])

        # set line length to 120, and check no violation on length 73
        rule = rules.BodyMaxLineLength({'line-length': 120})
        violations = rule.validate("a" * 73)
        self.assertIsNone(violations)

        # assert raise on 121
        expected_violation = rules.RuleViolation("B1", "Line exceeds max length (121>120)", "a" * 121)
        violations = rule.validate("a" * 121)
        self.assertListEqual(violations, [expected_violation])

    def test_trailing_whitespace(self):
        rule = rules.BodyTrailingWhitespace()

        # assert no error
        violations = rule.validate("a")
        self.assertIsNone(violations)

        # trailing space
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", "a ")
        violations = rule.validate("a ")
        self.assertListEqual(violations, [expected_violation])

        # trailing tab
        expected_violation = rules.RuleViolation("B2", "Line has trailing whitespace", "a\t")
        violations = rule.validate("a\t")
        self.assertListEqual(violations, [expected_violation])

    def test_hard_tabs(self):
        rule = rules.BodyHardTab()

        # assert no error
        violations = rule.validate("This is a test")
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = rules.RuleViolation("B3", "Line contains hard tab characters (\\t)", "This is a\ttest")
        violations = rule.validate("This is a\ttest")
        self.assertListEqual(violations, [expected_violation])

    def test_body_first_line_empty(self):
        rule = rules.BodyFirstLineEmpty()

        # assert no error
        violations = rule.validate(["", "This is the second body line"])
        self.assertIsNone(violations)

        # contains hard tab
        expected_violation = rules.RuleViolation("B4", "Second line is not empty", "not empty", 2)
        violations = rule.validate(["not empty", "This is the second body line"])
        self.assertListEqual(violations, [expected_violation])
