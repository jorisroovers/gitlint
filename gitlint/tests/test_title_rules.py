from gitlint.tests.base import BaseTestCase
from gitlint.rules import TitleMaxLength, TitleTrailingWhitespace, TitleHardTab, RuleViolation


class TitleRuleTests(BaseTestCase):
    def test_title_max_line_length(self):
        rule = TitleMaxLength()

        # assert no error
        violation = rule.validate("a" * 80)
        self.assertIsNone(violation)

        # assert error on line length > 81
        expected_violation = RuleViolation("T1", "Title exceeds max length (81>80)", "a" * 81)
        violation = rule.validate("a" * 81)
        self.assertEqual(violation, expected_violation)

        # set line length to 120, and check no violation on length 81
        rule = TitleMaxLength({'line-length': 120})
        violation = rule.validate("a" * 81)
        self.assertIsNone(violation)

        # assert raise on 121
        expected_violation = RuleViolation("T1", "Title exceeds max length (121>120)", "a" * 121)
        violation = rule.validate("a" * 121)
        self.assertEqual(violation, expected_violation)

    def test_trailing_whitespace(self):
        rule = TitleTrailingWhitespace()

        # assert no error
        violation = rule.validate("a")
        self.assertIsNone(violation)

        # trailing space
        expected_violation = RuleViolation("T2", "Title has trailing whitespace", "a ")
        violation = rule.validate("a ")
        self.assertEqual(violation, expected_violation)

        # trailing tab
        expected_violation = RuleViolation("T2", "Title has trailing whitespace", "a\t")
        violation = rule.validate("a\t")
        self.assertEqual(violation, expected_violation)

    def test_hard_tabs(self):
        rule = TitleHardTab()

        # assert no error
        violation = rule.validate("This is a test")
        self.assertIsNone(violation)

        # contains hard tab
        expected_violation = RuleViolation("T4", "Title contains hard tab characters (\\t)", "This is a\ttest")
        violation = rule.validate("This is a\ttest")
        self.assertEqual(violation, expected_violation)
