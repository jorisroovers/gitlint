from gitlint.config import LintConfig
from gitlint.contrib.rules.conventional_commit import ConventionalCommit
from gitlint.rules import RuleViolation
from gitlint.tests.base import BaseTestCase


class ContribConventionalCommitTests(BaseTestCase):
    def test_enable(self):
        # Test that rule can be enabled in config
        for rule_ref in ["CT1", "contrib-title-conventional-commits"]:
            config = LintConfig()
            config.contrib = [rule_ref]
            self.assertIn(ConventionalCommit(), config.rules)

    def test_conventional_commits(self):
        rule = ConventionalCommit()

        # No violations when using a correct type and format
        for type in [
            "fix",
            "feat",
            "chore",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "revert",
            "ci",
            "build",
        ]:
            violations = rule.validate(type + ": föo", None)
            self.assertListEqual([], violations)

        # assert violation on wrong type
        expected_violation = RuleViolation(
            "CT1",
            "Title does not start with one of fix, feat, chore, docs, style, refactor, perf, test, revert, ci, build",
            "bår: foo",
        )
        violations = rule.validate("bår: foo", None)
        self.assertListEqual([expected_violation], violations)

        # assert violation when use strange chars after correct type
        expected_violation = RuleViolation(
            "CT1",
            "Title does not start with one of fix, feat, chore, docs, style, refactor, perf, test, revert, ci, build",
            "feat_wrong_chars: föo",
        )
        violations = rule.validate("feat_wrong_chars: föo", None)
        self.assertListEqual([expected_violation], violations)

        # assert violation when use strange chars after correct type
        expected_violation = RuleViolation(
            "CT1",
            "Title does not start with one of fix, feat, chore, docs, style, refactor, perf, test, revert, ci, build",
            "feat_wrong_chars(scope): föo",
        )
        violations = rule.validate("feat_wrong_chars(scope): föo", None)
        self.assertListEqual([expected_violation], violations)

        # assert violation on wrong format
        expected_violation = RuleViolation(
            "CT1",
            "Title does not follow ConventionalCommits.org format 'type(optional-scope): description'",
            "fix föo",
        )
        violations = rule.validate("fix föo", None)
        self.assertListEqual([expected_violation], violations)

        # assert no violation when use ! for breaking changes without scope
        violations = rule.validate("feat!: föo", None)
        self.assertListEqual([], violations)

        # assert no violation when use ! for breaking changes with scope
        violations = rule.validate("fix(scope)!: föo", None)
        self.assertListEqual([], violations)

        # assert no violation when adding new type
        rule = ConventionalCommit({"types": ["föo", "bär"]})
        for typ in ["föo", "bär"]:
            violations = rule.validate(typ + ": hür dur", None)
            self.assertListEqual([], violations)

        # assert violation when using incorrect type when types have been reconfigured
        violations = rule.validate("fix: hür dur", None)
        expected_violation = RuleViolation("CT1", "Title does not start with one of föo, bär", "fix: hür dur")
        self.assertListEqual([expected_violation], violations)

        # assert no violation when adding new type named with numbers
        rule = ConventionalCommit({"types": ["föo123", "123bär"]})
        for typ in ["föo123", "123bär"]:
            violations = rule.validate(typ + ": hür dur", None)
            self.assertListEqual([], violations)

        # assert violation if scope is not in scopes
        rule = ConventionalCommit({"scopes": ["foo", "bar"]})
        violations = rule.validate("fix(baz): hellö", None)
        expected_violation = RuleViolation("CT1", "Scope is not one of foo, bar", "fix(baz): hellö")
        self.assertListEqual([expected_violation], violations)

        # assert no violation if scope is in scopes
        rule = ConventionalCommit({"scopes": ["foo", "bar"]})
        violations = rule.validate("fix(foo): hellö", None)
        self.assertListEqual([], violations)

        # assert no violation if scopes is empty
        rule = ConventionalCommit({"scopes": []})
        violations = rule.validate("fix(scope): hellö", None)
        self.assertListEqual([], violations)

        # assert violation if scope is required but not specified
        rule = ConventionalCommit({"require-scope": True})
        violations = rule.validate("fix: hellö", None)
        expected_violation = RuleViolation("CT1", "Scope is required", "fix: hellö")
        self.assertListEqual([expected_violation], violations)

        # assert no violation if scope is not required and not specified
        rule = ConventionalCommit({"require-scope": False})
        violations = rule.validate("fix: hellö", None)
        self.assertListEqual([], violations)
