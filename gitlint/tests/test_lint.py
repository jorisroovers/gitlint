# -*- coding: utf-8 -*-

from io import StringIO

from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.tests.base import BaseTestCase
from gitlint.lint import GitLinter
from gitlint.rules import RuleViolation, TitleMustNotContainWord
from gitlint.config import LintConfig, LintConfigBuilder


class LintTests(BaseTestCase):

    def test_lint_sample1(self):
        linter = GitLinter(LintConfig())
        gitcontext = self.gitcontext(self.get_sample("commit_message/sample1"))
        violations = linter.lint(gitcontext.commits[-1])
        expected_errors = [RuleViolation("T3", "Title has trailing punctuation (.)",
                                         "Commit title contåining 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                         "Commit title contåining 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("B4", "Second line is not empty", "This line should be empty", 2),
                           RuleViolation("B1", "Line exceeds max length (135>80)",
                                         "This is the first line of the commit message body and it is meant to test " +
                                         "a line that exceeds the maximum line length of 80 characters.", 3),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a tråiling space. ", 4),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing tab.\t", 5),
                           RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                         "This line has a trailing tab.\t", 5)]

        self.assertListEqual(violations, expected_errors)

    def test_lint_sample2(self):
        linter = GitLinter(LintConfig())
        gitcontext = self.gitcontext(self.get_sample("commit_message/sample2"))
        violations = linter.lint(gitcontext.commits[-1])
        expected = [RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                  "Just a title contåining WIP", 1),
                    RuleViolation("B6", "Body message is missing", None, 3)]

        self.assertListEqual(violations, expected)

    def test_lint_sample3(self):
        linter = GitLinter(LintConfig())
        gitcontext = self.gitcontext(self.get_sample("commit_message/sample3"))
        violations = linter.lint(gitcontext.commits[-1])

        title = " Commit title containing 'WIP', \tleading and tråiling whitespace and longer than 72 characters."
        expected = [RuleViolation("T1", "Title exceeds max length (95>72)", title, 1),
                    RuleViolation("T3", "Title has trailing punctuation (.)", title, 1),
                    RuleViolation("T4", "Title contains hard tab characters (\\t)", title, 1),
                    RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)", title, 1),
                    RuleViolation("T6", "Title has leading whitespace", title, 1),
                    RuleViolation("B4", "Second line is not empty", "This line should be empty", 2),
                    RuleViolation("B1", "Line exceeds max length (101>80)",
                                  "This is the first line is meånt to test a line that exceeds the maximum line " +
                                  "length of 80 characters.", 3),
                    RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing space. ", 4),
                    RuleViolation("B2", "Line has trailing whitespace", "This line has a tråiling tab.\t", 5),
                    RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                  "This line has a tråiling tab.\t", 5)]

        self.assertListEqual(violations, expected)

    def test_lint_sample4(self):
        commit = self.gitcommit(self.get_sample("commit_message/sample4"))
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_commit(commit)
        linter = GitLinter(config_builder.build())
        violations = linter.lint(commit)
        # expect no violations because sample4 has a 'gitlint: disable line'
        expected = []
        self.assertListEqual(violations, expected)

    def test_lint_sample5(self):
        commit = self.gitcommit(self.get_sample("commit_message/sample5"))
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_commit(commit)
        linter = GitLinter(config_builder.build())
        violations = linter.lint(commit)

        title = " Commit title containing 'WIP', \tleading and tråiling whitespace and longer than 72 characters."
        # expect only certain violations because sample5 has a 'gitlint-ignore: T3, T6, body-max-line-length'
        expected = [RuleViolation("T1", "Title exceeds max length (95>72)", title, 1),
                    RuleViolation("T4", "Title contains hard tab characters (\\t)", title, 1),
                    RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)", title, 1),
                    RuleViolation("B4", "Second line is not empty", "This line should be ëmpty", 2),
                    RuleViolation("B2", "Line has trailing whitespace", "This line has a tråiling space. ", 4),
                    RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing tab.\t", 5),
                    RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                  "This line has a trailing tab.\t", 5)]
        self.assertListEqual(violations, expected)

    def test_lint_meta(self):
        """ Lint sample2 but also add some metadata to the commit so we that gets linted as well """
        linter = GitLinter(LintConfig())
        gitcontext = self.gitcontext(self.get_sample("commit_message/sample2"))
        gitcontext.commits[0].author_email = "foo bår"
        violations = linter.lint(gitcontext.commits[-1])
        expected = [RuleViolation("M1", "Author email for commit is invalid", "foo bår", None),
                    RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                  "Just a title contåining WIP", 1),
                    RuleViolation("B6", "Body message is missing", None, 3)]

        self.assertListEqual(violations, expected)

    def test_lint_ignore(self):
        lint_config = LintConfig()
        lint_config.ignore = ["T1", "T3", "T4", "T5", "T6", "B1", "B2"]
        linter = GitLinter(lint_config)
        violations = linter.lint(self.gitcommit(self.get_sample("commit_message/sample3")))

        expected = [RuleViolation("B4", "Second line is not empty", "This line should be empty", 2),
                    RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                  "This line has a tråiling tab.\t", 5)]

        self.assertListEqual(violations, expected)

    def test_lint_configuration_rule(self):
        # Test that all rules are ignored because of matching regex
        lint_config = LintConfig()
        lint_config.set_rule_option("I1", "regex", "^Just a title(.*)")

        linter = GitLinter(lint_config)
        violations = linter.lint(self.gitcommit(self.get_sample("commit_message/sample2")))
        self.assertListEqual(violations, [])

        # Test ignoring only certain rules
        lint_config = LintConfig()
        lint_config.set_rule_option("I1", "regex", "^Just a title(.*)")
        lint_config.set_rule_option("I1", "ignore", "B6")

        linter = GitLinter(lint_config)
        violations = linter.lint(self.gitcommit(self.get_sample("commit_message/sample2")))

        # Normally we'd expect a B6 violation, but that one is skipped because of the specific ignore set above
        expected = [RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                  "Just a title contåining WIP", 1)]

        self.assertListEqual(violations, expected)

        # Test ignoring body lines
        lint_config = LintConfig()
        linter = GitLinter(lint_config)
        lint_config.set_rule_option("I3", "regex", "(.*)tråiling(.*)")
        violations = linter.lint(self.gitcommit(self.get_sample("commit_message/sample1")))
        expected_errors = [RuleViolation("T3", "Title has trailing punctuation (.)",
                                         "Commit title contåining 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)",
                                         "Commit title contåining 'WIP', as well as trailing punctuation.", 1),
                           RuleViolation("B4", "Second line is not empty", "This line should be empty", 2),
                           RuleViolation("B1", "Line exceeds max length (135>80)",
                                         "This is the first line of the commit message body and it is meant to test " +
                                         "a line that exceeds the maximum line length of 80 characters.", 3),
                           RuleViolation("B2", "Line has trailing whitespace", "This line has a trailing tab.\t", 4),
                           RuleViolation("B3", "Line contains hard tab characters (\\t)",
                                         "This line has a trailing tab.\t", 4)]

        self.assertListEqual(violations, expected_errors)

    def test_lint_special_commit(self):
        for commit_type in ["merge", "revert", "squash", "fixup"]:
            commit = self.gitcommit(self.get_sample(f"commit_message/{commit_type}"))
            lintconfig = LintConfig()
            linter = GitLinter(lintconfig)
            violations = linter.lint(commit)
            # Even though there are a number of violations in the commit message, they are ignored because
            # we are dealing with a merge commit
            self.assertListEqual(violations, [])

            # Check that we do see violations if we disable 'ignore-merge-commits'
            setattr(lintconfig, f"ignore_{commit_type}_commits", False)
            linter = GitLinter(lintconfig)
            violations = linter.lint(commit)
            self.assertTrue(len(violations) > 0)

    def test_lint_regex_rules(self):
        """ Additional test for title-match-regex, body-match-regex """
        commit = self.gitcommit(self.get_sample("commit_message/no-violations"))
        lintconfig = LintConfig()
        linter = GitLinter(lintconfig)
        violations = linter.lint(commit)
        # No violations by default
        self.assertListEqual(violations, [])

        # Matching regexes shouldn't be a problem
        rule_regexes = [("title-match-regex", "Tïtle$"), ("body-match-regex", "Sïgned-Off-By: (.*)$")]
        for rule_regex in rule_regexes:
            lintconfig.set_rule_option(rule_regex[0], "regex", rule_regex[1])
            violations = linter.lint(commit)
            self.assertListEqual(violations, [])

        # Non-matching regexes should return violations
        rule_regexes = [("title-match-regex", ), ("body-match-regex",)]
        lintconfig.set_rule_option("title-match-regex", "regex", "^Tïtle")
        lintconfig.set_rule_option("body-match-regex", "regex", "Sügned-Off-By: (.*)$")
        expected_violations = [RuleViolation("T7", "Title does not match regex (^Tïtle)", "Normal Commit Tïtle", 1),
                               RuleViolation("B8", "Body does not match regex (Sügned-Off-By: (.*)$)", None, 6)]
        violations = linter.lint(commit)
        self.assertListEqual(violations, expected_violations)

    def test_print_violations(self):
        violations = [RuleViolation("RULE_ID_1", "Error Messåge 1", "Violating Content 1", None),
                      RuleViolation("RULE_ID_2", "Error Message 2", "Violåting Content 2", 2)]
        linter = GitLinter(LintConfig())

        # test output with increasing verbosity
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 0
            linter.print_violations(violations)
            self.assertEqual("", stderr.getvalue())

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 1
            linter.print_violations(violations)
            expected = "-: RULE_ID_1\n2: RULE_ID_2\n"
            self.assertEqual(expected, stderr.getvalue())

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 2
            linter.print_violations(violations)
            expected = "-: RULE_ID_1 Error Messåge 1\n2: RULE_ID_2 Error Message 2\n"
            self.assertEqual(expected, stderr.getvalue())

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            linter.config.verbosity = 3
            linter.print_violations(violations)
            expected = "-: RULE_ID_1 Error Messåge 1: \"Violating Content 1\"\n" + \
                       "2: RULE_ID_2 Error Message 2: \"Violåting Content 2\"\n"
            self.assertEqual(expected, stderr.getvalue())

    def test_named_rules(self):
        """ Test that when named rules are present, both them and the original (non-named) rules executed """

        lint_config = LintConfig()
        for rule_name in ["my-ïd", "another-rule-ïd"]:
            rule_id = TitleMustNotContainWord.id + ":" + rule_name
            lint_config.rules.add_rule(TitleMustNotContainWord, rule_id)
            lint_config.set_rule_option(rule_id, "words", ["Föo"])
            linter = GitLinter(lint_config)

        violations = [RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)", "WIP: Föo bar", 1),
                      RuleViolation("T5:another-rule-ïd", "Title contains the word 'Föo' (case-insensitive)",
                                    "WIP: Föo bar", 1),
                      RuleViolation("T5:my-ïd", "Title contains the word 'Föo' (case-insensitive)",
                                    "WIP: Föo bar", 1)]
        self.assertListEqual(violations, linter.lint(self.gitcommit("WIP: Föo bar\n\nFoo bår hur dur bla bla")))

    def test_ignore_named_rules(self):
        """ Test that named rules can be ignored """

        # Add named rule to lint config
        config_builder = LintConfigBuilder()
        rule_id = TitleMustNotContainWord.id + ":my-ïd"
        config_builder.set_option(rule_id, "words", ["Föo"])
        lint_config = config_builder.build()
        linter = GitLinter(lint_config)
        commit = self.gitcommit("WIP: Föo bar\n\nFoo bår hur dur bla bla")

        # By default, we expect both the violations of the regular rule as well as the named rule to show up
        violations = [RuleViolation("T5", "Title contains the word 'WIP' (case-insensitive)", "WIP: Föo bar", 1),
                      RuleViolation("T5:my-ïd", "Title contains the word 'Föo' (case-insensitive)",
                                    "WIP: Föo bar", 1)]
        self.assertListEqual(violations, linter.lint(commit))

        # ignore regular rule: only named rule violations show up
        lint_config.ignore = ["T5"]
        self.assertListEqual(violations[1:], linter.lint(commit))

        # ignore named rule by id: only regular rule violations show up
        lint_config.ignore = [rule_id]
        self.assertListEqual(violations[:-1], linter.lint(commit))

        # ignore named rule by name: only regular rule violations show up
        lint_config.ignore = [TitleMustNotContainWord.name + ":my-ïd"]
        self.assertListEqual(violations[:-1], linter.lint(commit))
