# -*- coding: utf-8 -*-

from gitlint.tests.base import BaseTestCase

from gitlint.config import LintConfig, LintConfigBuilder, LintConfigError


class LintConfigBuilderTests(BaseTestCase):
    def test_set_from_commit_ignore_all(self):
        config = LintConfig()
        original_rules = config.rules
        original_rule_ids = [rule.id for rule in original_rules]

        config_builder = LintConfigBuilder()

        # nothing gitlint
        config_builder.set_config_from_commit(self.gitcommit(u"tëst\ngitlint\nfoo"))
        config = config_builder.build()
        self.assertListEqual(config.rules, original_rules)
        self.assertListEqual(config.ignore, [])

        # ignore all rules
        config_builder.set_config_from_commit(self.gitcommit(u"tëst\ngitlint-ignore: all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

        # ignore all rules, no space
        config_builder.set_config_from_commit(self.gitcommit(u"tëst\ngitlint-ignore:all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

        # ignore all rules, more spacing
        config_builder.set_config_from_commit(self.gitcommit(u"tëst\ngitlint-ignore: \t all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

    def test_set_from_commit_ignore_specific(self):
        # ignore specific rules
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_commit(self.gitcommit(u"tëst\ngitlint-ignore: T1, body-hard-tab"))
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
        foo_path = self.get_sample_path(u"föo")
        with self.assertRaisesRegex(LintConfigError, u"Invalid file path: {0}".format(foo_path)):
            config_builder.set_from_config_file(foo_path)

        # error during file parsing
        path = self.get_sample_path("config/no-sections")
        expected_error_msg = u"File contains no section headers."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.set_from_config_file(path)

        # non-existing rule
        path = self.get_sample_path("config/nonexisting-rule")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = u"No such rule 'föobar'"
        config_builder.set_from_config_file(path)
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

        # non-existing general option
        path = self.get_sample_path("config/nonexisting-general-option")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = u"'foo' is not a valid gitlint option"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

        # non-existing option
        path = self.get_sample_path("config/nonexisting-option")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = u"Rule 'title-max-length' has no option 'föobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

        # invalid option value
        path = self.get_sample_path("config/invalid-option-value")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = u"'föo' is not a valid value for option 'title-max-length.line-length'. " + \
                             u"Option 'line-length' must be a positive integer \(current value: 'föo'\)."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.build()

    def test_set_config_from_string_list(self):
        config = LintConfig()
        # assert some defaults
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 72)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 80)
        self.assertListEqual(config.get_rule_option('title-must-not-contain-word', 'words'), ["WIP"])
        self.assertEqual(config.verbosity, 3)

        # change and assert changes
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_string_list(['general.verbosity=1', 'title-max-length.line-length=60',
                                                    'body-max-line-length.line-length=120',
                                                    u"title-must-not-contain-word.words=håha"])

        config = config_builder.build()
        self.assertEqual(config.get_rule_option('title-max-length', 'line-length'), 60)
        self.assertEqual(config.get_rule_option('body-max-line-length', 'line-length'), 120)
        self.assertListEqual(config.get_rule_option('title-must-not-contain-word', 'words'), [u"håha"])
        self.assertEqual(config.verbosity, 1)

    def test_set_config_from_string_list_negative(self):
        config_builder = LintConfigBuilder()

        # assert error on incorrect rule - this happens at build time
        config_builder.set_config_from_string_list([u"föo.bar=1"])
        with self.assertRaisesRegex(LintConfigError, u"No such rule 'föo'"):
            config_builder.build()

        # no equal sign
        expected_msg = u"'föo.bar' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list([u"föo.bar"])

        # missing value
        expected_msg = u"'föo.bar=' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list([u"föo.bar="])

        # space instead of equal sign
        expected_msg = u"'föo.bar 1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list([u"föo.bar 1"])

        # no period between rule and option names
        expected_msg = u"'föobar=1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesRegex(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list([u'föobar=1'])

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
