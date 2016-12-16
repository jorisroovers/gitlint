from gitlint.tests.base import BaseTestCase

from gitlint.config import LintConfig, LintConfigBuilder, LintConfigError


class LintConfigBuilderTests(BaseTestCase):
    def test_set_from_commit_ignore_all(self):
        config = LintConfig()
        original_rules = config.rules
        original_rule_ids = [rule.id for rule in original_rules]

        config_builder = LintConfigBuilder()

        # nothing gitlint
        config_builder.set_config_from_commit(self.gitcommit("test\ngitlint\nfoo"))
        config = config_builder.build()
        self.assertListEqual(config.rules, original_rules)
        self.assertListEqual(config.ignore, [])

        # ignore all rules
        config_builder.set_config_from_commit(self.gitcommit("test\ngitlint-ignore: all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

        # ignore all rules, no space
        config_builder.set_config_from_commit(self.gitcommit("test\ngitlint-ignore:all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

        # ignore all rules, more spacing
        config_builder.set_config_from_commit(self.gitcommit("test\ngitlint-ignore: \t all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

    def test_set_from_commit_ignore_specific(self):
        # ignore specific rules
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_commit(self.gitcommit("test\ngitlint-ignore: T1, body-hard-tab"))
        config = config_builder.build()
        self.assertEqual(config.ignore, ["T1", "body-hard-tab"])

    def test_set_from_config_file(self):
        # regular config file load, no problems
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(self.get_sample_path("config/gitlintconfig"))
        config = config_builder.build()

        # Do some assertions on the config
        self.assertEqual(config.verbosity, 1)
        self.assertFalse(config.debug)
        self.assertFalse(config.ignore_merge_commits)
        self.assertIsNone(config.extra_path)
        self.assertEqual(config.ignore, ["title-trailing-whitespace", "B2"])

        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 20)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 30)

    def test_set_from_config_file_negative(self):
        config_builder = LintConfigBuilder()

        # bad config file load
        foo_path = self.get_sample_path("foo")
        with self.assertRaisesRegex(LintConfigError, "Invalid file path: {0}".format(foo_path)):
            config_builder.set_from_config_file(foo_path)

        # error during file parsing
        path = self.get_sample_path("config/no-sections")
        expected_error_msg = "File contains no section headers."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.set_from_config_file(path)

        # non-existing rule
        path = self.get_sample_path("config/nonexisting-rule")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "No such rule 'foobar'"
        config_builder.set_from_config_file(path)
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

        # non-existing general option
        path = self.get_sample_path("config/nonexisting-general-option")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "'foo' is not a valid gitlint option"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

        # non-existing option
        path = self.get_sample_path("config/nonexisting-option")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "Rule 'title-max-length' has no option 'foobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

        # invalid option value
        path = self.get_sample_path("config/invalid-option-value")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "'foo' is not a valid value for option 'title-max-length.line-length'. " + \
                             r"Option 'line-length' must be a positive integer \(current value: 'foo'\)."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

    def test_set_config_from_string_list(self):
        config = LintConfig()
        # assert some defaults
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 72)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 80)
        self.assertEqual(config.verbosity, 3)

        # change and assert changes
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_string_list(['general.verbosity=1', 'title-max-length.line-length=60',
                                                    'body-max-line-length.line-length=120'])

        config = config_builder.build()
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 60)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 120)
        self.assertEqual(config.verbosity, 1)

    def test_set_config_from_string_list_negative(self):
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_string_list(['foo.bar=1'])
        # assert error on incorrect rule - this happens at build time
        with self.assertRaisesRegex(LintConfigError, "No such rule 'foo'"):
            config_builder.build()

        # no equal sign
        expected_msg = "'foo.bar' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(['foo.bar'])

        # missing value
        expected_msg = "'foo.bar=' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(['foo.bar='])

        # space instead of equal sign
        expected_msg = "'foo.bar 1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(['foo.bar 1'])

        # no period between rule and option names
        expected_msg = "'foobar=1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(['foobar=1'])

    def test_rebuild_config(self):
        # normal config build
        config_builder = LintConfigBuilder()
        config_builder.set_option('general', 'verbosity', 3)
        lint_config = config_builder.build()
        self.assertEqual(lint_config.verbosity, 3)

        # check that existing config changes when we rebuild it
        existing_lintconfig = LintConfig()
        existing_lintconfig.verbosity = 2
        lint_config = config_builder.build(existing_lintconfig)
        self.assertEqual(lint_config.verbosity, 3)
