# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint import rules
from gitlint.config import LintConfig


class ConfigurationRuleTests(BaseTestCase):
    def test_ignore_by_title(self):
        commit = self.gitcommit("Releäse\n\nThis is the secōnd body line")

        # No regex specified -> Config shouldn't be changed
        rule = rules.IgnoreByTitle()
        config = LintConfig()
        rule.apply(config, commit)
        self.assertEqual(config, LintConfig())
        self.assert_logged([])  # nothing logged -> nothing ignored

        # Matching regex -> expect config to ignore all rules
        rule = rules.IgnoreByTitle({"regex": "^Releäse(.*)"})
        expected_config = LintConfig()
        expected_config.ignore = "all"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = "DEBUG: gitlint.rules Ignoring commit because of rule 'I1': " + \
            "Commit title 'Releäse' matches the regex '^Releäse(.*)', ignoring rules: all"
        self.assert_log_contains(expected_log_message)

        # Matching regex with specific ignore
        rule = rules.IgnoreByTitle({"regex": "^Releäse(.*)",
                                    "ignore": "T1,B2"})
        expected_config = LintConfig()
        expected_config.ignore = "T1,B2"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = "DEBUG: gitlint.rules Ignoring commit because of rule 'I1': " + \
            "Commit title 'Releäse' matches the regex '^Releäse(.*)', ignoring rules: T1,B2"

    def test_ignore_by_body(self):
        commit = self.gitcommit("Tïtle\n\nThis is\n a relëase body\n line")

        # No regex specified -> Config shouldn't be changed
        rule = rules.IgnoreByBody()
        config = LintConfig()
        rule.apply(config, commit)
        self.assertEqual(config, LintConfig())
        self.assert_logged([])  # nothing logged -> nothing ignored

        # Matching regex -> expect config to ignore all rules
        rule = rules.IgnoreByBody({"regex": "(.*)relëase(.*)"})
        expected_config = LintConfig()
        expected_config.ignore = "all"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = "DEBUG: gitlint.rules Ignoring commit because of rule 'I2': " + \
                               "Commit message line ' a relëase body' matches the regex '(.*)relëase(.*)'," + \
                               " ignoring rules: all"
        self.assert_log_contains(expected_log_message)

        # Matching regex with specific ignore
        rule = rules.IgnoreByBody({"regex": "(.*)relëase(.*)",
                                   "ignore": "T1,B2"})
        expected_config = LintConfig()
        expected_config.ignore = "T1,B2"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = "DEBUG: gitlint.rules Ignoring commit because of rule 'I2': " + \
            "Commit message line ' a relëase body' matches the regex '(.*)relëase(.*)', ignoring rules: T1,B2"
        self.assert_log_contains(expected_log_message)

    def test_ignore_by_author_name(self):
        commit = self.gitcommit("Tïtle\n\nThis is\n a relëase body\n line", author_name="Tëst nåme")

        # No regex specified -> Config shouldn't be changed
        rule = rules.IgnoreByAuthorName()
        config = LintConfig()
        rule.apply(config, commit)
        self.assertEqual(config, LintConfig())
        self.assert_logged([])  # nothing logged -> nothing ignored

        # Matching regex -> expect config to ignore all rules
        rule = rules.IgnoreByAuthorName({"regex": "(.*)ëst(.*)"})
        expected_config = LintConfig()
        expected_config.ignore = "all"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = ("DEBUG: gitlint.rules Ignoring commit because of rule 'I4': "
                                "Commit Author Name 'Tëst nåme' matches the regex '(.*)ëst(.*)',"
                                " ignoring rules: all")
        self.assert_log_contains(expected_log_message)

        # Matching regex with specific ignore
        rule = rules.IgnoreByAuthorName({"regex": "(.*)nåme", "ignore": "T1,B2"})
        expected_config = LintConfig()
        expected_config.ignore = "T1,B2"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = ("DEBUG: gitlint.rules Ignoring commit because of rule 'I4': "
                                "Commit Author Name 'Tëst nåme' matches the regex '(.*)nåme', ignoring rules: T1,B2")
        self.assert_log_contains(expected_log_message)

    def test_ignore_body_lines(self):
        commit1 = self.gitcommit("Tïtle\n\nThis is\n a relëase body\n line")
        commit2 = self.gitcommit("Tïtle\n\nThis is\n a relëase body\n line")

        # no regex specified, nothing should have happened:
        # commit and config should remain identical, log should be empty
        rule = rules.IgnoreBodyLines()
        config = LintConfig()
        rule.apply(config, commit1)
        self.assertEqual(commit1, commit2)
        self.assertEqual(config, LintConfig())
        self.assert_logged([])

        # Matching regex
        rule = rules.IgnoreBodyLines({"regex": "(.*)relëase(.*)"})
        config = LintConfig()
        rule.apply(config, commit1)
        # Our modified commit should be identical to a commit that doesn't contain the specific line
        expected_commit = self.gitcommit("Tïtle\n\nThis is\n line")
        # The original message isn't touched by this rule, this way we always have a way to reference back to it,
        # so assert it's not modified by setting it to the same as commit1
        expected_commit.message.original = commit1.message.original
        self.assertEqual(commit1, expected_commit)
        self.assertEqual(config, LintConfig())  # config shouldn't have been modified
        self.assert_log_contains("DEBUG: gitlint.rules Ignoring line ' a relëase body' because it " +
                                 "matches '(.*)relëase(.*)'")

        # Non-Matching regex: no changes expected
        commit1 = self.gitcommit("Tïtle\n\nThis is\n a relëase body\n line")
        rule = rules.IgnoreBodyLines({"regex": "(.*)föobar(.*)"})
        config = LintConfig()
        rule.apply(config, commit1)
        self.assertEqual(commit1, commit2)
        self.assertEqual(config, LintConfig())  # config shouldn't have been modified
