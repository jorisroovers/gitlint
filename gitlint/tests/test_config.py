from mock import patch

from gitlint import rules
from gitlint.config import LintConfig, LintConfigError, LintConfigGenerator, GITLINT_CONFIG_TEMPLATE_SRC_PATH
from gitlint.tests.base import BaseTestCase


class LintConfigTests(BaseTestCase):
    def test_get_rule(self):
        config = LintConfig()

        # get by id
        expected = rules.TitleMaxLength()
        rule = config.get_rule('T1')
        self.assertEqual(rule, expected)

        # get by name
        expected2 = rules.TitleTrailingWhitespace()
        rule = config.get_rule('title-trailing-whitespace')
        self.assertEqual(rule, expected2)

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
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config.set_rule_option('foobar', 'line-length', 60)

        # non-existing option
        expected_error_msg = "Rule 'title-max-length' has no option 'foobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config.set_rule_option('title-max-length', 'foobar', 60)

        # invalid option value
        expected_error_msg = "'foo' is not a valid value for option 'title-max-length.line-length'. " + \
                             r"Option 'line-length' must be a positive integer \(current value: 'foo'\)."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config.set_rule_option('title-max-length', 'line-length', "foo")

    def test_set_general_option(self):
        config = LintConfig()

        # Check that default general options are correct
        self.assertTrue(config.ignore_merge_commits)
        self.assertFalse(config.debug)
        self.assertEqual(config.verbosity, 3)
        active_rule_classes = [type(rule) for rule in config.rules]
        self.assertListEqual(active_rule_classes, config.rule_classes)

        # Check that we can change the general options
        # ignore
        config.set_general_option("ignore", "title-trailing-whitespace, B2")
        expected_ignored_rules = set([rules.BodyTrailingWhitespace, rules.TitleTrailingWhitespace])
        active_rule_classes = set(type(rule) for rule in config.rules)  # redetermine active rule classes
        expected_active_rule_classes = set(config.rule_classes) - expected_ignored_rules
        self.assertSetEqual(active_rule_classes, expected_active_rule_classes)

        # verbosity
        config.set_general_option("verbosity", 1)
        self.assertEqual(config.verbosity, 1)

        # ignore_merge_commit
        config.set_general_option("ignore-merge-commits", "false")
        self.assertFalse(config.ignore_merge_commits)

        # debug
        config.set_general_option("debug", "true")
        self.assertTrue(config.debug)

        # extra_path
        config.set_general_option("extra-path", self.get_rule_rules_path())
        self.assertEqual(config.extra_path, self.get_rule_rules_path())
        # reset value (this is a different code path)
        config.set_general_option("extra-path", self.SAMPLES_DIR)
        self.assertEqual(config.extra_path, self.SAMPLES_DIR)

    def test_set_general_option_negative(self):
        config = LintConfig()

        with self.assertRaisesRegex(LintConfigError, "'foo' is not a valid gitlint option"):
            config.set_general_option("foo", "bar")

        # invalid verbosity
        incorrect_values = [-1, "foo"]
        for value in incorrect_values:
            expected_msg = r"Option 'verbosity' must be a positive integer \(current value: '{0}'\)".format(value)
            with self.assertRaisesRegex(LintConfigError, expected_msg):
                config.verbosity = value

        incorrect_values = [4]
        for value in incorrect_values:
            with self.assertRaisesRegex(LintConfigError, "Option 'verbosity' must be set between 0 and 3"):
                config.verbosity = value

        # invalid ignore_merge_commits
        incorrect_values = [-1, 4, "foo"]
        for value in incorrect_values:
            with self.assertRaisesRegex(LintConfigError,
                                        r"Option 'ignore-merge-commits' must be either 'true' or 'false'"):
                config.ignore_merge_commits = value

        # invalid debug
        with self.assertRaisesRegex(LintConfigError, r"Option 'debug' must be either 'true' or 'false'"):
            config.debug = "foobar"

        # invalid extra-path
        with self.assertRaisesRegex(LintConfigError,
                                    r"Option extra_path must be an existing directory \(current value: 'foo/bar'\)"):
            config.extra_path = "foo/bar"

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
        with self.assertRaisesRegex(LintConfigError, "No such rule 'foo'"):
            config.apply_config_options(['foo.bar=1'])

        # no equal sign
        expected_msg = "'foo.bar' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config.apply_config_options(['foo.bar'])

        # missing value
        expected_msg = "'foo.bar=' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config.apply_config_options(['foo.bar='])

        # space instead of equal sign
        expected_msg = "'foo.bar 1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config.apply_config_options(['foo.bar 1'])

        # no period between rule and option names
        expected_msg = "'foobar=1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config.apply_config_options(['foobar=1'])

    def test_load_config_from_file(self):
        # regular config file load, no problems
        config = LintConfig.load_from_file(self.get_sample_path("config/gitlintconfig"))

        # Do some assertions on the config
        self.assertEqual(config.verbosity, 1)
        self.assertFalse(config.debug)
        self.assertFalse(config.ignore_merge_commits)

        # ignored rules
        expected_ignored_rules = set([rules.BodyTrailingWhitespace, rules.TitleTrailingWhitespace])
        active_rule_classes = set(type(rule) for rule in config.rules)
        self.assertSetEqual(set(config.rule_classes) - expected_ignored_rules, active_rule_classes)

        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 20)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 30)
        self.assertIsNone(config.get_rule('title-trailing-whitespace'))

    def test_load_config_from_file_negative(self):
        # bad config file load
        foo_path = self.get_sample_path("foo")
        with self.assertRaisesRegex(LintConfigError, "Invalid file path: {0}".format(foo_path)):
            LintConfig.load_from_file(foo_path)

        # error during file parsing
        path = self.get_sample_path("config/no-sections")
        expected_error_msg = "File contains no section headers."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # non-existing rule
        path = self.get_sample_path("config/nonexisting-rule")
        expected_error_msg = "No such rule 'foobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # non-existing general option
        path = self.get_sample_path("config/nonexisting-general-option")
        expected_error_msg = "'foo' is not a valid gitlint option"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # non-existing option
        path = self.get_sample_path("config/nonexisting-option")
        expected_error_msg = "Rule 'title-max-length' has no option 'foobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

        # invalid option value
        path = self.get_sample_path("config/invalid-option-value")
        expected_error_msg = "'foo' is not a valid value for option 'title-max-length.line-length'. " + \
                             r"Option 'line-length' must be a positive integer \(current value: 'foo'\)."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            LintConfig.load_from_file(path)

    def test_gitcontext_ignore_all(self):
        config = LintConfig()
        original_rules = config.rules

        # nothing gitlint
        context = self.gitcontext("test\ngitlint\nfoo")
        config.apply_config_from_commit(context.commits[-1])
        self.assertListEqual(config.rules, original_rules)

        # ignore all rules
        context = self.gitcontext("test\ngitlint-ignore: all\nfoo")
        config.apply_config_from_commit(context.commits[-1])
        self.assertEqual(config.rules, [])

        # ignore all rules, no space
        config = LintConfig()
        context = self.gitcontext("test\ngitlint-ignore:all\nfoo")
        config.apply_config_from_commit(context.commits[-1])
        self.assertEqual(config.rules, [])

        # ignore all rules, more spacing
        config = LintConfig()
        context = self.gitcontext("test\ngitlint-ignore: \t all\nfoo")
        config.apply_config_from_commit(context.commits[-1])
        self.assertEqual(config.rules, [])

    def test_gitcontext_ignore_specific(self):
        # ignore specific rules
        config = LintConfig()
        context = self.gitcontext("test\ngitlint-ignore: T1, body-hard-tab")
        config.apply_config_from_commit(context.commits[-1])
        expected_rules = [rule for rule in config.rules if rule.id not in ["T1", "body-hard-tab"]]
        self.assertEqual(config.rules, expected_rules)


class LintConfigGeneratorTests(BaseTestCase):
    @staticmethod
    @patch('gitlint.config.shutil.copyfile')
    def test_install_commit_msg_hook_negative(copy):
        LintConfigGenerator.generate_config("foo/bar/test")
        copy.assert_called_with(GITLINT_CONFIG_TEMPLATE_SRC_PATH, "foo/bar/test")
