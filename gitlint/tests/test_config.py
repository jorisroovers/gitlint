from gitlint.tests.base import BaseTestCase
from gitlint.config import LintConfig, LintConfigError

from gitlint import rules


class LintConfigTests(BaseTestCase):
    def test_get_rule_by_name_or_id(self):
        config = LintConfig()

        # get by id
        expected = rules.TitleMaxLength()
        rule = config.get_rule_by_name_or_id('T1')
        self.assertEqual(rule, expected)

        # get by name
        expected = rules.TitleTrailingWhitespace()
        rule = config.get_rule_by_name_or_id('title-trailing-whitespace')
        self.assertEqual(rule, expected)

        # get non-existing
        rule = config.get_rule_by_name_or_id('foo')
        self.assertIsNone(rule)

    def test_load_config_from_file(self):
        # regular config file load, no problems
        config = LintConfig.load_from_file(self.get_sample_path("gitlintconfig"))

        # Do some assertions on the config
        self.assertEqual(config.verbosity, 1)
        self.assertEqual(config.get_rule_by_name_or_id('title-max-length').options['line-length'].value, 20)
        self.assertEqual(config.get_rule_by_name_or_id('body-max-line-length').options['line-length'].value, 30)

    def test_negative_load_config_from_file(self):
        # bad config file load
        foo_path = self.get_sample_path("foo")
        with self.assertRaisesRegexp(LintConfigError, "Invalid file path: {0}".format(foo_path)):
            LintConfig.load_from_file(foo_path)

        # error during file parsing
        bad_markdowlint_path = self.get_sample_path("badgitlintconfig")
        expected_error_msg = "Error during config file parsing: File contains no section headers."
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(bad_markdowlint_path)
