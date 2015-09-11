from gitlint.tests.base import BaseTestCase

from gitlint.lint import GitLinter
from gitlint.rules import RuleViolation
from gitlint.config import LintConfig


class RuleOptionTests(BaseTestCase):
    def test_lint(self):
        linter = GitLinter(LintConfig())
        violations = linter.lint_commit_message(self.get_sample("commit_message/sample1"))
        expected_errors = [RuleViolation("T3", "Title has trailing punctuation (.)",
                                         "Commit title containing 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                         "Commit title containing 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("B1", "Line exceeds max length (135>80)",
                                         "This is the first line of the commit message body and it is meant to test " +
                                         "a line that exceeds the maximum line length of 80 characters.", 3),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing space. ", 4),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing tab.\t", 5),
                           RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                         "This line has a trailing tab.\t", 5),
                           ]

        self.assertListEqual(violations, expected_errors)
