# -*- coding: utf-8 -*-

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint import rules
from gitlint.config import LintConfig, LintConfigError, LintConfigGenerator, GITLINT_CONFIG_TEMPLATE_SRC_PATH
from gitlint import options
from gitlint.tests.base import BaseTestCase, ustr


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
        rule = config.get_rule(u'föo')
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
        expected_error_msg = u"No such rule 'föobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config.set_rule_option(u'föobar', u'lïne-length', 60)

        # non-existing option
        expected_error_msg = u"Rule 'title-max-length' has no option 'föobar'"
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config.set_rule_option('title-max-length', u'föobar', 60)

        # invalid option value
        expected_error_msg = u"'föo' is not a valid value for option 'title-max-length.line-length'. " + \
                             u"Option 'line-length' must be a positive integer (current value: 'föo')."
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config.set_rule_option('title-max-length', 'line-length', u"föo")

    def test_set_general_option(self):
        config = LintConfig()

        # Check that default general options are correct
        self.assertTrue(config.ignore_merge_commits)
        self.assertTrue(config.ignore_fixup_commits)
        self.assertTrue(config.ignore_squash_commits)

        self.assertFalse(config.debug)
        self.assertEqual(config.verbosity, 3)
        active_rule_classes = tuple(type(rule) for rule in config.rules)
        self.assertTupleEqual(active_rule_classes, config.default_rule_classes)

        # ignore - set by string
        config.set_general_option("ignore", "title-trailing-whitespace, B2")
        self.assertEqual(config.ignore, ["title-trailing-whitespace", "B2"])

        # ignore - set by list
        config.set_general_option("ignore", ["T1", "B3"])
        self.assertEqual(config.ignore, ["T1", "B3"])

        # verbosity
        config.set_general_option("verbosity", 1)
        self.assertEqual(config.verbosity, 1)

        # ignore_merge_commit
        config.set_general_option("ignore-merge-commits", "false")
        self.assertFalse(config.ignore_merge_commits)

        # ignore_fixup_commit
        config.set_general_option("ignore-fixup-commits", "false")
        self.assertFalse(config.ignore_fixup_commits)

        # ignore_squash_commit
        config.set_general_option("ignore-squash-commits", "false")
        self.assertFalse(config.ignore_squash_commits)

        # ignore_revert_commit
        config.set_general_option("ignore-revert-commits", "false")
        self.assertFalse(config.ignore_revert_commits)

        # debug
        config.set_general_option("debug", "true")
        self.assertTrue(config.debug)

        # target
        config.set_general_option("target", self.SAMPLES_DIR)
        self.assertEqual(config.target, self.SAMPLES_DIR)

        # extra_path has its own test: test_extra_path and test_extra_path_negative
        # contrib has its own tests: test_contrib and test_contrib_negative

    def test_contrib(self):
        config = LintConfig()
        contrib_rules = ["contrib-title-conventional-commits", "CC1"]
        config.set_general_option("contrib", ",".join(contrib_rules))
        self.assertEqual(config.contrib, contrib_rules)

        # Check contrib-title-conventional-commits contrib rule
        actual_rule = config.get_rule("contrib-title-conventional-commits")
        self.assertTrue(actual_rule.is_contrib)

        self.assertEqual(ustr(type(actual_rule)), "<class 'conventional_commit.ConventionalCommit'>")
        self.assertEqual(actual_rule.id, 'CT1')
        self.assertEqual(actual_rule.name, u'contrib-title-conventional-commits')
        self.assertEqual(actual_rule.target, rules.CommitMessageTitle)

        expected_rule_option = options.ListOption(
            "types",
            ["fix", "feat", "chore", "docs", "style", "refactor", "perf", "test", "revert"],
            "Comma separated list of allowed commit types.",
        )

        self.assertListEqual(actual_rule.options_spec, [expected_rule_option])
        self.assertDictEqual(actual_rule.options, {'types': expected_rule_option})

        # Check contrib-body-requires-signed-off-by contrib rule
        actual_rule = config.get_rule("contrib-body-requires-signed-off-by")
        self.assertTrue(actual_rule.is_contrib)

        self.assertEqual(ustr(type(actual_rule)), "<class 'signedoff_by.SignedOffBy'>")
        self.assertEqual(actual_rule.id, 'CC1')
        self.assertEqual(actual_rule.name, u'contrib-body-requires-signed-off-by')

        # reset value (this is a different code path)
        config.set_general_option("contrib", "contrib-body-requires-signed-off-by")
        self.assertEqual(actual_rule, config.get_rule("contrib-body-requires-signed-off-by"))
        self.assertIsNone(config.get_rule("contrib-title-conventional-commits"))

        # empty value
        config.set_general_option("contrib", "")
        self.assertListEqual(config.contrib, [])

    def test_contrib_negative(self):
        config = LintConfig()
        # non-existent contrib rule
        with self.assertRaisesRegex(LintConfigError, u"No contrib rule with id or name 'föo' found."):
            config.contrib = u"contrib-title-conventional-commits,föo"

        # UserRuleError, RuleOptionError should be re-raised as LintConfigErrors
        side_effects = [rules.UserRuleError(u"üser-rule"), options.RuleOptionError(u"rüle-option")]
        for side_effect in side_effects:
            with patch('gitlint.config.rule_finder.find_rule_classes', side_effect=side_effect):
                with self.assertRaisesRegex(LintConfigError, ustr(side_effect)):
                    config.contrib = u"contrib-title-conventional-commits"

    def test_extra_path(self):
        config = LintConfig()

        config.set_general_option("extra-path", self.get_user_rules_path())
        self.assertEqual(config.extra_path, self.get_user_rules_path())
        actual_rule = config.get_rule('UC1')
        self.assertTrue(actual_rule.is_user_defined)
        self.assertEqual(ustr(type(actual_rule)), "<class 'my_commit_rules.MyUserCommitRule'>")
        self.assertEqual(actual_rule.id, 'UC1')
        self.assertEqual(actual_rule.name, u'my-üser-commit-rule')
        self.assertEqual(actual_rule.target, None)
        expected_rule_option = options.IntOption('violation-count', 1, u"Number of violåtions to return")
        self.assertListEqual(actual_rule.options_spec, [expected_rule_option])
        self.assertDictEqual(actual_rule.options, {'violation-count': expected_rule_option})

        # reset value (this is a different code path)
        config.set_general_option("extra-path", self.SAMPLES_DIR)
        self.assertEqual(config.extra_path, self.SAMPLES_DIR)
        self.assertIsNone(config.get_rule("UC1"))

    def test_extra_path_negative(self):
        config = LintConfig()
        regex = u"Option extra-path must be either an existing directory or file (current value: 'föo/bar')"
        # incorrect extra_path
        with self.assertRaisesRegex(LintConfigError, regex):
            config.extra_path = u"föo/bar"

        # extra path contains classes with errors
        with self.assertRaisesRegex(LintConfigError,
                                    "User-defined rule class 'MyUserLineRule' must have a 'validate' method"):
            config.extra_path = self.get_sample_path("user_rules/incorrect_linerule")

    def test_set_general_option_negative(self):
        config = LintConfig()

        # Note that we shouldn't test whether we can set unicode because python just doesn't allow unicode attributes
        with self.assertRaisesRegex(LintConfigError, "'foo' is not a valid gitlint option"):
            config.set_general_option("foo", u"bår")

        # try setting _config_path, this is a real attribute of LintConfig, but the code should prevent it from
        # being set
        with self.assertRaisesRegex(LintConfigError, "'_config_path' is not a valid gitlint option"):
            config.set_general_option("_config_path", u"bår")

        # invalid verbosity`
        incorrect_values = [-1, u"föo"]
        for value in incorrect_values:
            expected_msg = u"Option 'verbosity' must be a positive integer (current value: '{0}')".format(value)
            with self.assertRaisesRegex(LintConfigError, expected_msg):
                config.verbosity = value

        incorrect_values = [4]
        for value in incorrect_values:
            with self.assertRaisesRegex(LintConfigError, "Option 'verbosity' must be set between 0 and 3"):
                config.verbosity = value

        # invalid ignore_xxx_commits
        ignore_attributes = ["ignore_merge_commits", "ignore_fixup_commits", "ignore_squash_commits",
                             "ignore_revert_commits"]
        incorrect_values = [-1, 4, u"föo"]
        for attribute in ignore_attributes:
            for value in incorrect_values:
                option_name = attribute.replace("_", "-")
                with self.assertRaisesRegex(LintConfigError,
                                            "Option '{0}' must be either 'true' or 'false'".format(option_name)):
                    setattr(config, attribute, value)

        # invalid ignore -> not here because ignore is a ListOption which converts everything to a string before
        # splitting which means it it will accept just about everything

        # invalid debug
        with self.assertRaisesRegex(LintConfigError, "Option 'debug' must be either 'true' or 'false'"):
            config.debug = u"föobar"

        # extra-path has its own negative test

        # invalid target
        with self.assertRaisesRegex(LintConfigError,
                                    u"Option target must be an existing directory (current value: 'föo/bar')"):
            config.target = u"föo/bar"

    def test_ignore_independent_from_rules(self):
        # Test that the lintconfig rules are not modified when setting config.ignore
        # This was different in the past, this test is mostly here to catch regressions
        config = LintConfig()
        original_rules = config.rules
        config.ignore = ["T1", "T2"]
        self.assertEqual(config.ignore, ["T1", "T2"])
        self.assertListEqual(config.rules, original_rules)


class LintConfigGeneratorTests(BaseTestCase):
    @staticmethod
    @patch('gitlint.config.shutil.copyfile')
    def test_install_commit_msg_hook_negative(copy):
        LintConfigGenerator.generate_config(u"föo/bar/test")
        copy.assert_called_with(GITLINT_CONFIG_TEMPLATE_SRC_PATH, u"föo/bar/test")
