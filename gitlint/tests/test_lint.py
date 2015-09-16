from gitlint.tests.base import BaseTestCase

from gitlint.lint import GitLinter
from gitlint.rules import RuleViolation
from gitlint.config import LintConfig
from gitlint.git import GitContext

from mock import patch

from StringIO import StringIO


class RuleOptionTests(BaseTestCase):
    def test_lint(self):
        linter = GitLinter(LintConfig())
        gitcontext = GitContext()
        gitcontext.set_commit_msg(self.get_sample("commit_message/sample1"))
        violations = linter.lint(gitcontext)
        expected_errors = [RuleViolation("T3", "Title has trailing punctuation (.)",
                                         "Commit title containing 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                         "Commit title containing 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("B4", "Second line is not empty", "This line should be empty", 2),
                           RuleViolation("B1", "Line exceeds max length (135>80)",
                                         "This is the first line of the commit message body and it is meant to test " +
                                         "a line that exceeds the maximum line length of 80 characters.", 3),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing space. ", 4),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing tab.\t", 5),
                           RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                         "This line has a trailing tab.\t", 5),
                           ]

        self.assertListEqual(violations, expected_errors)

    def test_print_violations(self):
        violations = [RuleViolation("RULE_ID_1", "Error Message 1", "Violating Content 1", 1),
                      RuleViolation("RULE_ID_2", "Error Message 2", "Violating Content 2", 2)]
        linter = GitLinter(LintConfig())

        # test output with increasing verbosity
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 0
            linter.print_violations(violations)
            self.assertEqual("", stderr.getvalue())

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 1
            linter.print_violations(violations)
            expected = "1: RULE_ID_1\n2: RULE_ID_2\n"
            self.assertEqual(expected, stderr.getvalue())

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 2
            linter.print_violations(violations)
            expected = "1: RULE_ID_1 Error Message 1\n2: RULE_ID_2 Error Message 2\n"
            self.assertEqual(expected, stderr.getvalue())

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 3
            linter.print_violations(violations)
            expected = "1: RULE_ID_1 Error Message 1: \"Violating Content 1\"\n" + \
                       "2: RULE_ID_2 Error Message 2: \"Violating Content 2\"\n"
            self.assertEqual(expected, stderr.getvalue())
