from gitlint.rules import Rule, RuleViolation
from gitlint.tests.base import BaseTestCase


class RuleTests(BaseTestCase):
    def test_ruleviolation__str__(self):
        expected = '57: rule-ïd Tēst message: "Tēst content"'
        self.assertEqual(str(RuleViolation("rule-ïd", "Tēst message", "Tēst content", 57)), expected)

    def test_rule_equality(self):
        # Ensure rules are not equal if they differ on one of their attributes
        rule_attrs = ["id", "name", "target", "options"]
        for attr in rule_attrs:
            rule1 = Rule()
            rule2 = Rule()
            for attr2 in rule_attrs:
                setattr(rule1, attr2, "föo")
                setattr(rule2, attr2, "föo")
            self.assertEqual(rule1, rule2)
            setattr(rule1, attr, "åbc")
            self.assertNotEqual(rule1, rule2)

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
