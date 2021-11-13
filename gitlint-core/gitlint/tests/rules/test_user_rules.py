# -*- coding: utf-8 -*-

import os
import sys

from gitlint.tests.base import BaseTestCase
from gitlint.rule_finder import find_rule_classes, assert_valid_rule_class
from gitlint.rules import UserRuleError

from gitlint import options, rules


class UserRuleTests(BaseTestCase):
    def test_find_rule_classes(self):
        # Let's find some user classes!
        user_rule_path = self.get_sample_path("user_rules")
        classes = find_rule_classes(user_rule_path)

        # Compare string representations because we can't import MyUserCommitRule here since samples/user_rules is not
        # a proper python package
        # Note that the following check effectively asserts that:
        # - There is only 1 rule recognized and it is MyUserCommitRule
        # - Other non-python files in the directory are ignored
        # - Other members of the my_commit_rules module are ignored
        #  (such as func_should_be_ignored, global_variable_should_be_ignored)
        # - Rules are loaded non-recursively (user_rules/import_exception directory is ignored)
        self.assertEqual("[<class 'my_commit_rules.MyUserCommitRule'>]", str(classes))

        # Assert that we added the new user_rules directory to the system path and modules
        self.assertIn(user_rule_path, sys.path)
        self.assertIn("my_commit_rules", sys.modules)

        # Do some basic asserts on our user rule
        self.assertEqual(classes[0].id, "UC1")
        self.assertEqual(classes[0].name, "my-üser-commit-rule")
        expected_option = options.IntOption('violation-count', 1, "Number of violåtions to return")
        self.assertListEqual(classes[0].options_spec, [expected_option])
        self.assertTrue(hasattr(classes[0], "validate"))

        # Test that we can instantiate the class and can execute run the validate method and that it returns the
        # expected result
        rule_class = classes[0]()
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [rules.RuleViolation("UC1", "Commit violåtion 1", "Contënt 1", 1)])

        # Have it return more violations
        rule_class.options['violation-count'].value = 2
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [rules.RuleViolation("UC1", "Commit violåtion 1", "Contënt 1", 1),
                                          rules.RuleViolation("UC1", "Commit violåtion 2", "Contënt 2", 2)])

    def test_extra_path_specified_by_file(self):
        # Test that find_rule_classes can handle an extra path given as a file name instead of a directory
        user_rule_path = self.get_sample_path("user_rules")
        user_rule_module = os.path.join(user_rule_path, "my_commit_rules.py")
        classes = find_rule_classes(user_rule_module)

        rule_class = classes[0]()
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [rules.RuleViolation("UC1", "Commit violåtion 1", "Contënt 1", 1)])

    def test_rules_from_init_file(self):
        # Test that we can import rules that are defined in __init__.py files
        # This also tests that we can import rules from python packages. This use to cause issues with pypy
        # So this is also a regression test for that.
        user_rule_path = self.get_sample_path(os.path.join("user_rules", "parent_package"))
        classes = find_rule_classes(user_rule_path)

        # convert classes to strings and sort them so we can compare them
        class_strings = sorted([str(clazz) for clazz in classes])
        expected = ["<class 'my_commit_rules.MyUserCommitRule'>", "<class 'parent_package.InitFileRule'>"]
        self.assertListEqual(class_strings, expected)

    def test_empty_user_classes(self):
        # Test that we don't find rules if we scan a different directory
        user_rule_path = self.get_sample_path("config")
        classes = find_rule_classes(user_rule_path)
        self.assertListEqual(classes, [])

        # Importantly, ensure that the directory is not added to the syspath as this happens only when we actually
        # find modules
        self.assertNotIn(user_rule_path, sys.path)

    def test_failed_module_import(self):
        # test importing a bogus module
        user_rule_path = self.get_sample_path("user_rules/import_exception")
        # We don't check the entire error message because that is different based on the python version and underlying
        # operating system
        expected_msg = "Error while importing extra-path module 'invalid_python'"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            find_rule_classes(user_rule_path)

    def test_find_rule_classes_nonexisting_path(self):
        with self.assertRaisesMessage(UserRuleError, "Invalid extra-path: föo/bar"):
            find_rule_classes("föo/bar")

    def test_assert_valid_rule_class(self):
        class MyLineRuleClass(rules.LineRule):
            id = 'UC1'
            name = 'my-lïne-rule'
            target = rules.CommitMessageTitle

            def validate(self):
                pass

        class MyCommitRuleClass(rules.CommitRule):
            id = 'UC2'
            name = 'my-cömmit-rule'

            def validate(self):
                pass

        class MyConfigurationRuleClass(rules.ConfigurationRule):
            id = 'UC3'
            name = 'my-cönfiguration-rule'

            def apply(self):
                pass

        # Just assert that no error is raised
        self.assertIsNone(assert_valid_rule_class(MyLineRuleClass))
        self.assertIsNone(assert_valid_rule_class(MyCommitRuleClass))
        self.assertIsNone(assert_valid_rule_class(MyConfigurationRuleClass))

    def test_assert_valid_rule_class_negative(self):
        # general test to make sure that incorrect rules will raise an exception
        user_rule_path = self.get_sample_path("user_rules/incorrect_linerule")
        with self.assertRaisesMessage(UserRuleError,
                                      "User-defined rule class 'MyUserLineRule' must have a 'validate' method"):
            find_rule_classes(user_rule_path)

    def test_assert_valid_rule_class_negative_parent(self):
        # rule class must extend from LineRule or CommitRule
        class MyRuleClass:
            pass

        expected_msg = "User-defined rule class 'MyRuleClass' must extend from gitlint.rules.LineRule, " + \
                       "gitlint.rules.CommitRule or gitlint.rules.ConfigurationRule"
        with self.assertRaisesMessage(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_id(self):

        for parent_class in [rules.LineRule, rules.CommitRule]:

            class MyRuleClass(parent_class):
                pass

            # Rule class must have an id
            expected_msg = "User-defined rule class 'MyRuleClass' must have an 'id' attribute"
            with self.assertRaisesMessage(UserRuleError, expected_msg):
                assert_valid_rule_class(MyRuleClass)

            # Rule ids must be non-empty
            MyRuleClass.id = ""
            with self.assertRaisesMessage(UserRuleError, expected_msg):
                assert_valid_rule_class(MyRuleClass)

            # Rule ids must not start with one of the reserved id letters
            for letter in ["T", "R", "B", "M", "I"]:
                MyRuleClass.id = letter + "1"
                expected_msg = f"The id '{letter}' of 'MyRuleClass' is invalid. " + \
                               "Gitlint reserves ids starting with R,T,B,M,I"
                with self.assertRaisesMessage(UserRuleError, expected_msg):
                    assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_name(self):
        for parent_class in [rules.LineRule, rules.CommitRule]:

            class MyRuleClass(parent_class):
                id = "UC1"

            # Rule class must have a name
            expected_msg = "User-defined rule class 'MyRuleClass' must have a 'name' attribute"
            with self.assertRaisesMessage(UserRuleError, expected_msg):
                assert_valid_rule_class(MyRuleClass)

            # Rule names must be non-empty
            MyRuleClass.name = ""
            with self.assertRaisesMessage(UserRuleError, expected_msg):
                assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_option_spec(self):

        for parent_class in [rules.LineRule, rules.CommitRule]:

            class MyRuleClass(parent_class):
                id = "UC1"
                name = "my-rüle-class"

            # if set, option_spec must be a list of gitlint options
            MyRuleClass.options_spec = "föo"
            expected_msg = "The options_spec attribute of user-defined rule class 'MyRuleClass' must be a list " + \
                "of gitlint.options.RuleOption"
            with self.assertRaisesMessage(UserRuleError, expected_msg):
                assert_valid_rule_class(MyRuleClass)

            # option_spec is a list, but not of gitlint options
            MyRuleClass.options_spec = ["föo", 123]  # pylint: disable=bad-option-value,redefined-variable-type
            with self.assertRaisesMessage(UserRuleError, expected_msg):
                assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_validate(self):

        baseclasses = [rules.LineRule, rules.CommitRule]
        for clazz in baseclasses:
            class MyRuleClass(clazz):
                id = "UC1"
                name = "my-rüle-class"

            with self.assertRaisesMessage(UserRuleError,
                                          "User-defined rule class 'MyRuleClass' must have a 'validate' method"):
                assert_valid_rule_class(MyRuleClass)

            # validate attribute - not a method
            MyRuleClass.validate = "föo"
            with self.assertRaisesMessage(UserRuleError,
                                          "User-defined rule class 'MyRuleClass' must have a 'validate' method"):
                assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_apply(self):
        class MyRuleClass(rules.ConfigurationRule):
            id = "UCR1"
            name = "my-rüle-class"

        expected_msg = "User-defined Configuration rule class 'MyRuleClass' must have an 'apply' method"
        with self.assertRaisesMessage(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # validate attribute - not a method
        MyRuleClass.validate = "föo"
        with self.assertRaisesMessage(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_target(self):
        class MyRuleClass(rules.LineRule):
            id = "UC1"
            name = "my-rüle-class"

            def validate(self):
                pass

        # no target
        expected_msg = "The target attribute of the user-defined LineRule class 'MyRuleClass' must be either " + \
                       "gitlint.rules.CommitMessageTitle or gitlint.rules.CommitMessageBody"
        with self.assertRaisesMessage(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # invalid target
        MyRuleClass.target = "föo"
        with self.assertRaisesMessage(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # valid target, no exception should be raised
        MyRuleClass.target = rules.CommitMessageTitle  # pylint: disable=bad-option-value,redefined-variable-type
        self.assertIsNone(assert_valid_rule_class(MyRuleClass))
