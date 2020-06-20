
# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.rules import RuleViolation
from gitlint.contrib.rules.conventional_commit import ConventionalCommit
from gitlint.config import LintConfig


class ContribConventionalCommitTests(BaseTestCase):

    def test_enable(self):
        # Test that rule can be enabled in config
        for rule_ref in ['CT1', 'contrib-title-conventional-commits']:
            config = LintConfig()
            config.contrib = [rule_ref]
            self.assertIn(ConventionalCommit(), config.rules)

    def test_conventional_commits(self):
        rule = ConventionalCommit()

        # No violations when using a correct type and format
        for type in ["fix", "feat", "chore", "docs", "style", "refactor", "perf", "test", "revert", "ci", "build"]:
            violations = rule.validate(type + u": föo", None)
            self.assertListEqual([], violations)

        # assert violation on wrong type
        expected_violation = RuleViolation("CT1", "Title does not start with one of fix, feat, chore, docs,"
                                                  " style, refactor, perf, test, revert, ci, build", u"bår: foo")
        violations = rule.validate(u"bår: foo", None)
        self.assertListEqual([expected_violation], violations)

        # assert violation on wrong format
        expected_violation = RuleViolation("CT1", "Title does not follow ConventionalCommits.org format "
                                                  "'type(optional-scope): description'", u"fix föo")
        violations = rule.validate(u"fix föo", None)
        self.assertListEqual([expected_violation], violations)

        # assert no violation when adding new type
        rule = ConventionalCommit({'types': [u"föo", u"bär"]})
        for typ in [u"föo", u"bär"]:
            violations = rule.validate(typ + u": hür dur", None)
            self.assertListEqual([], violations)

        # assert violation when using incorrect type when types have been reconfigured
        violations = rule.validate(u"fix: hür dur", None)
        expected_violation = RuleViolation("CT1", u"Title does not start with one of föo, bär", u"fix: hür dur")
        self.assertListEqual([expected_violation], violations)
