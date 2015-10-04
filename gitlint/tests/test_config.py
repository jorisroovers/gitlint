from gitlint.tests.base import BaseTestCase
from gitlint.config import LintConfig, LintConfigError
from gitlint.git import GitContext

from gitlint import rules


class LintConfigTests(BaseTestCase):
    def test_get_rule(self):
        config = LintConfig()

        # get by id
        expected = rules.TitleMaxLength()
        rule = config.get_rule('T1')
        self.assertEqual(rule, expected)

        # get by name
        expected = rules.TitleTrailingWhitespace()
        rule = config.get_rule('title-trailing-whitespace')
        self.assertEqual(rule, expected)

        # get non-existing
        rule = config.get_rule('foo')
        self.assertIsNone(rule)

    def test_set_rule_option(self):
        config = LintConfig()

        # assert default title line-length
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 72)

        # change line length and assert it is set
        config.set_rule_option('title-max-length', 'line-length', 60)
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 60)

    def test_set_rule_option_negative(self):
        config = LintConfig()

        # non-existing rule
        expected_error_msg = "No such rule 'foobar'"
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            config.set_rule_option('foobar', 'line-length', 60)

        # non-existing option
        expected_error_msg = "Rule 'title-max-length' has no option 'foobar'"
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            config.set_rule_option('title-max-length', 'foobar', 60)

        # invalid option value
        expected_error_msg = "'foo' is not a valid value for option 'title-max-length.line-length'. " + \
                             "Option 'line-length' must be a positive integer \(current value: 'foo'\)."
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            config.set_rule_option('title-max-length', 'line-length', "foo")

        # invalid verbosity
        with self.assertRaisesRegexp(LintConfigError, "verbosity must be set between 0 and 3"):
            config.verbosity = -1
        with self.assertRaisesRegexp(LintConfigError, "verbosity must be set between 0 and 3"):
            config.verbosity = 4

    def test_apply_config_options(self):
        config = LintConfig()
        # assert some defaults
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 72)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 80)
        self.assertEqual(config.verbosity, 3)

        # change and assert changes
        config.apply_config_options(['general.verbosity=1', 'title-max-length.line-length=60',
                                     'body-max-line-length.line-length=120'])
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 60)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 120)
        self.assertEqual(config.verbosity, 1)

    def test_apply_config_options_negative(self):
        config = LintConfig()

        # assert error on incorrect rule
        with self.assertRaisesRegexp(LintConfigError, "No such rule 'foo'"):
            config.apply_config_options(['foo.bar=1'])

        # no equal sign
        expected_msg = "'foo.bar' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegexp(LintConfigError, expected_msg):
            config.apply_config_options(['foo.bar'])

        # missing value
        expected_msg = "'foo.bar=' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegexp(LintConfigError, expected_msg):
            config.apply_config_options(['foo.bar='])

        # space instead of equal sign
        expected_msg = "'foo.bar 1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegexp(LintConfigError, expected_msg):
            config.apply_config_options(['foo.bar 1'])

        # no period between rule and option names
        expected_msg = "'foobar=1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegexp(LintConfigError, expected_msg):
            config.apply_config_options(['foobar=1'])

    def test_load_config_from_file(self):
        # regular config file load, no problems
        config = LintConfig.load_from_file(self.get_sample_path("config/gitlintconfig"))

        # Do some assertions on the config
        self.assertEqual(config.verbosity, 1)
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 20)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 30)
        self.assertIsNone(config.get_rule('title-trailing-whitespace'))

    def test_load_config_from_file_negative(self):
        # bad config file load
        foo_path = self.get_sample_path("foo")
        with self.assertRaisesRegexp(LintConfigError, "Invalid file path: {0}".format(foo_path)):
            LintConfig.load_from_file(foo_path)

        # error during file parsing
        path = self.get_sample_path("config/no-sections")
        expected_error_msg = "File contains no section headers."
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # non-existing rule
        path = self.get_sample_path("config/nonexisting-rule")
        expected_error_msg = "No such rule 'foobar'"
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # non-existing option
        path = self.get_sample_path("config/nonexisting-option")
        expected_error_msg = "Rule 'title-max-length' has no option 'foobar'"
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # invalid option value
        path = self.get_sample_path("config/invalid-option-value")
        expected_error_msg = "'foo' is not a valid value for option 'title-max-length.line-length'. " + \
                             "Option 'line-length' must be a positive integer \(current value: 'foo'\)."
        with self.assertRaisesRegexp(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

    def test_gitcontext_ignore_all(self):
        config = LintConfig()
        original_rules = config.rules

        # nothing gitlint
        context = GitContext()
        context.set_commit_msg("test\ngitlint\nfoo")
        config.apply_config_from_gitcontext(context)
        self.assertListEqual(config.rules, original_rules)

        # ignore all rules
        context = GitContext()
        context.set_commit_msg("test\ngitlint-ignore: all\nfoo")
        config.apply_config_from_gitcontext(context)
        self.assertEqual(config.rules, [])

        # ignore all rules, no space
        config = LintConfig()
        context.set_commit_msg("test\ngitlint-ignore:all\nfoo")
        config.apply_config_from_gitcontext(context)
        self.assertEqual(config.rules, [])

        # ignore all rules, more spacing
        config = LintConfig()
        context.set_commit_msg("test\ngitlint-ignore: \t all\nfoo")
        config.apply_config_from_gitcontext(context)
        self.assertEqual(config.rules, [])

    def test_gitcontext_ignore_specific(self):
        # ignore specific rules
        config = LintConfig()
        context = GitContext()
        context.set_commit_msg("test\ngitlint-ignore: T1, body-hard-tab")
        config.apply_config_from_gitcontext(context)
        expected_rules = [rule for rule in config.rules if rule.id not in ["T1", "body-hard-tab"]]
        self.assertEqual(config.rules, expected_rules)
