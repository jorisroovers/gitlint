from gitlint.tests.base import BaseTestCase
from gitlint.rules import RuleViolation
from gitlint.contrib.rules.disallow_cleanup_commits import DisallowCleanupCommits

from gitlint.config import LintConfig


class ContribDisallowCleanupCommitsTest(BaseTestCase):
    def test_enable(self):
        # Test that rule can be enabled in config
        for rule_ref in ["CC2", "contrib-disallow-cleanup-commits"]:
            config = LintConfig()
            config.contrib = [rule_ref]
            self.assertIn(DisallowCleanupCommits(), config.rules)

    def test_disallow_fixup_squash_commit(self):
        # No violations when no 'fixup!' line and no 'squash!' line is present
        rule = DisallowCleanupCommits()
        violations = rule.validate(self.gitcommit("Föobar\n\nMy Body"))
        self.assertListEqual(violations, [])

        # Assert violation when 'fixup!' in title
        violations = rule.validate(self.gitcommit("fixup! Föobar\n\nMy Body"))
        expected_violation = RuleViolation("CC2", "Fixup commits are not allowed", line_nr=1)
        self.assertListEqual(violations, [expected_violation])

        # Assert violation when 'squash!' in title
        violations = rule.validate(self.gitcommit("squash! Föobar\n\nMy Body"))
        expected_violation = RuleViolation("CC2", "Squash commits are not allowed", line_nr=1)
        self.assertListEqual(violations, [expected_violation])

        # Assert violation when 'amend!' in title
        violations = rule.validate(self.gitcommit("amend! Föobar\n\nMy Body"))
        expected_violation = RuleViolation("CC2", "Amend commits are not allowed", line_nr=1)
        self.assertListEqual(violations, [expected_violation])
