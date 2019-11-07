# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint import rules
from gitlint.config import LintConfig


class ConfigurationRuleTests(BaseTestCase):
    def test_ignore_by_title(self):
        commit = self.gitcommit(u"Releäse\n\nThis is the secōnd body line")

        # No regex specified -> Config shouldn't be changed
        rule = rules.IgnoreByTitle()
        config = LintConfig()
        rule.apply(config, commit)
        self.assertEqual(config, LintConfig())
        self.assert_logged([])  # nothing logged -> nothing ignored

        # Matching regex -> expect config to ignore all rules
        rule = rules.IgnoreByTitle({"regex": u"^Releäse(.*)"})
        expected_config = LintConfig()
        expected_config.ignore = "all"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = u"DEBUG: gitlint.rules Ignoring commit because of rule 'I1': " + \
            u"Commit title 'Releäse' matches the regex '^Releäse(.*)', ignoring rules: all"
        self.assert_log_contains(expected_log_message)

        # Matching regex with specific ignore
        rule = rules.IgnoreByTitle({"regex": u"^Releäse(.*)",
                                    "ignore": "T1,B2"})
        expected_config = LintConfig()
        expected_config.ignore = "T1,B2"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = u"DEBUG: gitlint.rules Ignoring commit because of rule 'I1': " + \
            u"Commit title 'Releäse' matches the regex '^Releäse(.*)', ignoring rules: T1,B2"

    def test_ignore_by_body(self):
        commit = self.gitcommit(u"Tïtle\n\nThis is\n a relëase body\n line")

        # No regex specified -> Config shouldn't be changed
        rule = rules.IgnoreByBody()
        config = LintConfig()
        rule.apply(config, commit)
        self.assertEqual(config, LintConfig())
        self.assert_logged([])  # nothing logged -> nothing ignored

        # Matching regex -> expect config to ignore all rules
        rule = rules.IgnoreByBody({"regex": u"(.*)relëase(.*)"})
        expected_config = LintConfig()
        expected_config.ignore = "all"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = u"DEBUG: gitlint.rules Ignoring commit because of rule 'I2': " + \
                               u"Commit message line ' a relëase body' matches the regex '(.*)relëase(.*)'," + \
                               u" ignoring rules: all"
        self.assert_log_contains(expected_log_message)

        # Matching regex with specific ignore
        rule = rules.IgnoreByBody({"regex": u"(.*)relëase(.*)",
                                   "ignore": "T1,B2"})
        expected_config = LintConfig()
        expected_config.ignore = "T1,B2"
        rule.apply(config, commit)
        self.assertEqual(config, expected_config)

        expected_log_message = u"DEBUG: gitlint.rules Ignoring commit because of rule 'I1': " + \
            u"Commit message line ' a relëase body' matches the regex '(.*)relëase(.*)', ignoring rules: T1,B2"
