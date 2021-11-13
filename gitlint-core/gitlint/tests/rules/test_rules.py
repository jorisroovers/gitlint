# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import Rule, RuleViolation


class RuleTests(BaseTestCase):

    def test_rule_equality(self):
        self.assertEqual(Rule(), Rule())
        # Ensure rules are not equal if they differ on their attributes
        for attr in ["id", "name", "target", "options"]:
            rule = Rule()
            setattr(rule, attr, "åbc")
            self.assertNotEqual(Rule(), rule)

    def test_rule_log(self):
        rule = Rule()
        rule.log.debug("Tēst message")
        self.assert_log_contains("DEBUG: gitlint.rules Tēst message")

    def test_rule_violation_equality(self):
        violation1 = RuleViolation("ïd1", "My messåge", "My cöntent", 1)
        self.object_equality_test(violation1, ["rule_id", "message", "content", "line_nr"])
