from mock import patch

from gitlint import rules
from gitlint.config import LintConfig, LintConfigError, LintConfigGenerator, GITLINT_CONFIG_TEMPLATE_SRC_PATH
from gitlint.options import IntOption
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

        # debug
        config.set_general_option("debug", "true")
        self.assertTrue(config.debug)

        # target
        config.set_general_option("target", self.SAMPLES_DIR)
        self.assertEqual(config.target, self.SAMPLES_DIR)

        # extra_path has its own test: test_extra_path

    def test_extra_path(self):
        config = LintConfig()

        config.set_general_option("extra-path", self.get_rule_rules_path())
        self.assertEqual(config.extra_path, self.get_rule_rules_path())
        actual_rule = config.get_rule('TUC1')
        self.assertTrue(actual_rule.user_defined)
        self.assertEqual(str(type(actual_rule)), "<class 'my_commit_rules.MyUserCommitRule'>")
        self.assertEqual(actual_rule.id, 'TUC1')
        self.assertEqual(actual_rule.name, 'my-user-commit-rule')
        self.assertEqual(actual_rule.target, None)
        expected_rule_option = IntOption('violation-count', 1, "Number of violations to return")
        self.assertListEqual(actual_rule.options_spec, [expected_rule_option])
        self.assertDictEqual(actual_rule.options, {'violation-count': expected_rule_option})

        # reset value (this is a different code path)
        config.set_general_option("extra-path", self.SAMPLES_DIR)
        self.assertEqual(config.extra_path, self.SAMPLES_DIR)
        self.assertIsNone(config.get_rule("TUC1"))

    def test_set_general_option_negative(self):
        config = LintConfig()

        with self.assertRaisesRegex(LintConfigError, "'foo' is not a valid gitlint option"):
            config.set_general_option("foo", "bar")

        # try setting _config_path, this is a real attribute of LintConfig, but the code should prevent it from
        # being set
        with self.assertRaisesRegex(LintConfigError, "'_config_path' is not a valid gitlint option"):
            config.set_general_option("_config_path", "bar")

        # invalid verbosity`
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

        # invalid ignore -> not here because ignore is a ListOption which converts everything to a string before
        # splitting which means it it will accept just about everything

        # invalid debug
        with self.assertRaisesRegex(LintConfigError, r"Option 'debug' must be either 'true' or 'false'"):
            config.debug = "foobar"

        # invalid extra-path
        with self.assertRaisesRegex(LintConfigError,
                                    r"Option extra-path must be an existing directory \(current value: 'foo/bar'\)"):
            config.extra_path = "foo/bar"

        # invalid target
        with self.assertRaisesRegex(LintConfigError,
                                    r"Option target must be an existing directory \(current value: 'foo/bar'\)"):
            config.target = "foo/bar"

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
        LintConfigGenerator.generate_config("foo/bar/test")
        copy.assert_called_with(GITLINT_CONFIG_TEMPLATE_SRC_PATH, "foo/bar/test")
