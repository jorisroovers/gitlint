
# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import RuleViolation
from gitlint.contrib.rules.signedoff_by import SignedOffBy

from gitlint.config import LintConfig


class ContribSignedOffByTests(BaseTestCase):

    def test_enable(self):
        # Test that rule can be enabled in config
        for rule_ref in ['CC1', 'contrib-body-requires-signed-off-by']:
            config = LintConfig()
            config.contrib = [rule_ref]
            self.assertIn(SignedOffBy(), config.rules)

    def test_signedoff_by(self):
        # No violations when 'Signed-Off-By' line is present
        rule = SignedOffBy()
        violations = rule.validate(self.gitcommit(u"Föobar\n\nMy Body\nSigned-Off-By: John Smith"))
        self.assertListEqual([], violations)

        # Assert violation when no 'Signed-Off-By' line is present
        violations = rule.validate(self.gitcommit(u"Föobar\n\nMy Body"))
        expected_violation = RuleViolation("CC1", "Body does not contain a 'Signed-Off-By' line", line_nr=1)
        self.assertListEqual(violations, [expected_violation])

        # Assert violation when no 'Signed-Off-By' in title but not in body
        violations = rule.validate(self.gitcommit(u"Signed-Off-By\n\nFöobar"))
        self.assertListEqual(violations, [expected_violation])
