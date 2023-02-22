from gitlint.rules import Rule, RuleViolation
from gitlint.tests.base import BaseTestCase


class RuleTests(BaseTestCase):
    def test_ruleviolation__str__(self):
        expected = "57: rule-ïd Tēst message: \"Tēst content\""
        self.assertEqual(str(RuleViolation("rule-ïd", "Tēst message", "Tēst content", 57)), expected)

    def test_rule_equality(self):
        self.assertEqual(Rule(), Rule())
        # Ensure rules are not equal if they differ on their attributes
        for attr in ["id", "name", "target", "options"]:
            rule = Rule()
            setattr(rule, attr, "åbc")
            self.assertNotEqual(Rule(), rule)

    def test_rule_log(self):
        rule = Rule()
        self.assertIsNone(rule._log)
        rule.log.debug("Tēst message")
        self.assert_log_contains("DEBUG: gitlint.rules Tēst message")
        
        # Assert the same logger is reused when logging multiple messages
        log = rule._log
        rule.log.debug("Anöther message")
        self.assertEqual(log, rule._log)
        self.assert_log_contains("DEBUG: gitlint.rules Anöther message")



    def test_rule_violation_equality(self):
        violation1 = RuleViolation("ïd1", "My messåge", "My cöntent", 1)
        self.object_equality_test(violation1, ["rule_id", "message", "content", "line_nr"])
