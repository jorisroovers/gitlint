import copy

from gitlint.tests.base import BaseTestCase

from gitlint.config import LintConfig, LintConfigBuilder, LintConfigError

from gitlint import rules


class LintConfigBuilderTests(BaseTestCase):
    def test_set_option(self):
        config_builder = LintConfigBuilder()
        config = config_builder.build()

        # assert some defaults
        self.assertEqual(config.get_rule_option("title-max-length", "line-length"), 72)
        self.assertEqual(config.get_rule_option("body-max-line-length", "line-length"), 80)
        self.assertListEqual(config.get_rule_option("title-must-not-contain-word", "words"), ["WIP"])
        self.assertEqual(config.verbosity, 3)

        # Make some changes and check blueprint
        config_builder.set_option("title-max-length", "line-length", 100)
        config_builder.set_option("general", "verbosity", 2)
        config_builder.set_option("title-must-not-contain-word", "words", ["foo", "bar"])
        expected_blueprint = {
            "title-must-not-contain-word": {"words": ["foo", "bar"]},
            "title-max-length": {"line-length": 100},
            "general": {"verbosity": 2},
        }
        self.assertDictEqual(config_builder._config_blueprint, expected_blueprint)

        # Build config and verify that the changes have occurred and no other changes
        config = config_builder.build()
        self.assertEqual(config.get_rule_option("title-max-length", "line-length"), 100)
        self.assertEqual(config.get_rule_option("body-max-line-length", "line-length"), 80)  # should be unchanged
        self.assertListEqual(config.get_rule_option("title-must-not-contain-word", "words"), ["foo", "bar"])
        self.assertEqual(config.verbosity, 2)

    def test_set_from_commit_ignore_all(self):
        config = LintConfig()
        original_rules = config.rules
        original_rule_ids = [rule.id for rule in original_rules]

        config_builder = LintConfigBuilder()

        # nothing gitlint
        config_builder.set_config_from_commit(self.gitcommit("tëst\ngitlint\nfoo"))
        config = config_builder.build()
        self.assertSequenceEqual(config.rules, original_rules)
        self.assertListEqual(config.ignore, [])

        # ignore all rules
        config_builder.set_config_from_commit(self.gitcommit("tëst\ngitlint-ignore: all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

        # ignore all rules, no space
        config_builder.set_config_from_commit(self.gitcommit("tëst\ngitlint-ignore:all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

        # ignore all rules, more spacing
        config_builder.set_config_from_commit(self.gitcommit("tëst\ngitlint-ignore: \t all\nfoo"))
        config = config_builder.build()
        self.assertEqual(config.ignore, original_rule_ids)

    def test_set_from_commit_ignore_specific(self):
        # ignore specific rules
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_commit(self.gitcommit("tëst\ngitlint-ignore: T1, body-hard-tab"))
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

        self.assertEqual(config.get_rule_option("title-max-length", "line-length"), 20)
        self.assertEqual(config.get_rule_option("body-max-line-length", "line-length"), 30)

    def test_set_from_config_file_negative(self):
        config_builder = LintConfigBuilder()

        # bad config file load
        foo_path = self.get_sample_path("föo")
        expected_error_msg = f"Invalid file path: {foo_path}"
        with self.assertRaisesMessage(LintConfigError, expected_error_msg):
            config_builder.set_from_config_file(foo_path)

        # error during file parsing
        path = self.get_sample_path("config/no-sections")
        expected_error_msg = "File contains no section headers."
        # We only match the start of the message here, since the exact message can vary depending on platform
        with self.assertRaisesRegex(LintConfigError, expected_error_msg):
            config_builder.set_from_config_file(path)

        # non-existing rule
        path = self.get_sample_path("config/nonexisting-rule")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "No such rule 'föobar'"
        with self.assertRaisesMessage(LintConfigError, expected_error_msg):
            config_builder.build()

        # non-existing general option
        path = self.get_sample_path("config/nonexisting-general-option")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "'foo' is not a valid gitlint option"
        with self.assertRaisesMessage(LintConfigError, expected_error_msg):
            config_builder.build()

        # non-existing option
        path = self.get_sample_path("config/nonexisting-option")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = "Rule 'title-max-length' has no option 'föobar'"
        with self.assertRaisesMessage(LintConfigError, expected_error_msg):
            config_builder.build()

        # invalid option value
        path = self.get_sample_path("config/invalid-option-value")
        config_builder = LintConfigBuilder()
        config_builder.set_from_config_file(path)
        expected_error_msg = (
            "'föo' is not a valid value for option 'title-max-length.line-length'. "
            "Option 'line-length' must be a positive integer (current value: 'föo')."
        )
        with self.assertRaisesMessage(LintConfigError, expected_error_msg):
            config_builder.build()

    def test_set_config_from_string_list(self):
        config = LintConfig()

        # change and assert changes
        config_builder = LintConfigBuilder()
        config_builder.set_config_from_string_list(
            [
                "general.verbosity=1",
                "title-max-length.line-length=60",
                "body-max-line-length.line-length=120",
                "title-must-not-contain-word.words=håha",
            ]
        )

        config = config_builder.build()
        self.assertEqual(config.get_rule_option("title-max-length", "line-length"), 60)
        self.assertEqual(config.get_rule_option("body-max-line-length", "line-length"), 120)
        self.assertListEqual(config.get_rule_option("title-must-not-contain-word", "words"), ["håha"])
        self.assertEqual(config.verbosity, 1)

    def test_set_config_from_string_list_negative(self):
        config_builder = LintConfigBuilder()

        # assert error on incorrect rule - this happens at build time
        config_builder.set_config_from_string_list(["föo.bar=1"])
        with self.assertRaisesMessage(LintConfigError, "No such rule 'föo'"):
            config_builder.build()

        # no equal sign
        expected_msg = "'föo.bar' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesMessage(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(["föo.bar"])

        # missing value
        expected_msg = "'föo.bar=' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesMessage(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(["föo.bar="])

        # space instead of equal sign
        expected_msg = "'föo.bar 1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesMessage(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(["föo.bar 1"])

        # no period between rule and option names
        expected_msg = "'föobar=1' is an invalid configuration option. Use '<rule>.<option>=<value>'"
        with self.assertRaisesMessage(LintConfigError, expected_msg):
            config_builder.set_config_from_string_list(["föobar=1"])

    def test_rebuild_config(self):
        # normal config build
        config_builder = LintConfigBuilder()
        config_builder.set_option("general", "verbosity", 3)
        lint_config = config_builder.build()
        self.assertEqual(lint_config.verbosity, 3)

        # check that existing config gets overwritten when we pass it to a configbuilder with different options
        existing_lintconfig = LintConfig()
        existing_lintconfig.verbosity = 2
        lint_config = config_builder.build(existing_lintconfig)
        self.assertEqual(lint_config.verbosity, 3)
        self.assertEqual(existing_lintconfig.verbosity, 3)

    def test_clone(self):
        config_builder = LintConfigBuilder()
        config_builder.set_option("general", "verbosity", 2)
        config_builder.set_option("title-max-length", "line-length", 100)
        expected = {"title-max-length": {"line-length": 100}, "general": {"verbosity": 2}}
        self.assertDictEqual(config_builder._config_blueprint, expected)

        # Clone and verify that the blueprint is the same as the original
        cloned_builder = config_builder.clone()
        self.assertDictEqual(cloned_builder._config_blueprint, expected)

        # Modify the original and make sure we're not modifying the clone (i.e. check that the copy is a deep copy)
        config_builder.set_option("title-max-length", "line-length", 120)
        self.assertDictEqual(cloned_builder._config_blueprint, expected)

    def test_named_rules(self):
        # Store a copy of the default rules from the config, so we can reference it later
        config_builder = LintConfigBuilder()
        config = config_builder.build()
        default_rules = copy.deepcopy(config.rules)
        self.assertEqual(default_rules, config.rules)  # deepcopy should be equal

        # Add a named rule by setting an option in the config builder that follows the named rule pattern
        # Assert that whitespace in the rule name is stripped
        rule_qualifiers = [
            "T7:my-extra-rüle",
            " T7 :   my-extra-rüle  ",
            "\tT7:\tmy-extra-rüle\t",
            "T7:\t\n  \tmy-extra-rüle\t\n\n",
            "title-match-regex:my-extra-rüle",
        ]
        for rule_qualifier in rule_qualifiers:
            config_builder = LintConfigBuilder()
            config_builder.set_option(rule_qualifier, "regex", "föo")

            expected_rules = copy.deepcopy(default_rules)
            my_rule = rules.TitleRegexMatches({"regex": "föo"})
            my_rule.id = rules.TitleRegexMatches.id + ":my-extra-rüle"
            my_rule.name = rules.TitleRegexMatches.name + ":my-extra-rüle"
            expected_rules._rules["T7:my-extra-rüle"] = my_rule
            self.assertEqual(config_builder.build().rules, expected_rules)

            # assert that changing an option on the newly added rule is passed correctly to the RuleCollection
            # we try this with all different rule qualifiers to ensure they all are normalized and map
            # to the same rule
            for other_rule_qualifier in rule_qualifiers:
                cb = config_builder.clone()
                cb.set_option(other_rule_qualifier, "regex", other_rule_qualifier + "bōr")
                # before setting the expected rule option value correctly, the RuleCollection should be different
                self.assertNotEqual(cb.build().rules, expected_rules)
                # after setting the option on the expected rule, it should be equal
                my_rule.options["regex"].set(other_rule_qualifier + "bōr")
                self.assertEqual(cb.build().rules, expected_rules)
                my_rule.options["regex"].set("wrong")

    def test_named_rules_negative(self):
        # T7 = title-match-regex
        # Invalid rule name
        for invalid_name in ["", " ", "    ", "\t", "\n", "å b", "å:b", "åb:", ":åb"]:
            config_builder = LintConfigBuilder()
            config_builder.set_option(f"T7:{invalid_name}", "regex", "tëst")
            expected_msg = f"The rule-name part in 'T7:{invalid_name}' cannot contain whitespace, colons or be empty"
            with self.assertRaisesMessage(LintConfigError, expected_msg):
                config_builder.build()

        # Invalid parent rule name
        config_builder = LintConfigBuilder()
        config_builder.set_option("Ž123:foöbar", "fåke-option", "fåke-value")
        with self.assertRaisesMessage(LintConfigError, "No such rule 'Ž123' (named rule: 'Ž123:foöbar')"):
            config_builder.build()

        # Invalid option name (this is the same as with regular rules)
        config_builder = LintConfigBuilder()
        config_builder.set_option("T7:foöbar", "blå", "my-rëgex")
        with self.assertRaisesMessage(LintConfigError, "Rule 'T7:foöbar' has no option 'blå'"):
            config_builder.build()
