# -*- coding: utf-8 -*-

import sys

from gitlint.tests.base import BaseTestCase
from gitlint.user_rules import find_rule_classes, assert_valid_rule_class, UserRuleError
from gitlint.utils import ustr

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
        self.assertEqual("[<class 'my_commit_rules.MyUserCommitRule'>]", ustr(classes))

        # Assert that we added the new user_rules directory to the system path and modules
        self.assertIn(user_rule_path, sys.path)
        self.assertIn("my_commit_rules", sys.modules)

        # # Do some basic asserts on our user rule
        self.assertEqual(classes[0].id, "UC1")
        self.assertEqual(classes[0].name, u"my-üser-commit-rule")
        expected_option = options.IntOption('violation-count', 1, u"Number of violåtions to return")
        self.assertListEqual(classes[0].options_spec, [expected_option])
        self.assertTrue(hasattr(classes[0], "validate"))

        # Test that we can instantiate the class and can execute run the validate method and that it returns the
        # expected result
        rule_class = classes[0]()
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [rules.RuleViolation("UC1", u"Commit violåtion 1", u"Contënt 1", 1)])

        # Have it return more violations
        rule_class.options['violation-count'].value = 2
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [rules.RuleViolation("UC1", u"Commit violåtion 1", u"Contënt 1", 1),
                                          rules.RuleViolation("UC1", u"Commit violåtion 2", u"Contënt 2", 2)])

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
        # When searching an non-existing path, we expect an OSError. That's fine because this case will be caught by
        # the CLI (you cannot specify a non-existing directory). What we do here is just assert that we indeed
        # get an OSError (so we guard against regressions).
        with self.assertRaisesRegex(OSError, "No such file or directory"):
            find_rule_classes(u"föo/bar")

    def test_assert_valid_rule_class(self):
        class MyLineRuleClass(rules.LineRule):
            id = 'UC1'
            name = u'my-lïne-rule'
            target = rules.CommitMessageTitle

            def validate(self):
                pass

        class MyCommitRuleClass(rules.CommitRule):
            id = 'UC2'
            name = u'my-cömmit-rule'

            def validate(self):
                pass

        # Just assert that no error is raised
        self.assertIsNone(assert_valid_rule_class(MyLineRuleClass))
        self.assertIsNone(assert_valid_rule_class(MyCommitRuleClass))

    def test_assert_valid_rule_class_negative(self):
        # general test to make sure that incorrect rules will raise an exception
        user_rule_path = self.get_sample_path("user_rules/incorrect_linerule")
        with self.assertRaisesRegex(UserRuleError,
                                    "User-defined rule class 'MyUserLineRule' must have a 'validate' method"):
            find_rule_classes(user_rule_path)

    def test_assert_valid_rule_class_negative_parent(self):
        # rule class must extend from LineRule or CommitRule
        class MyRuleClass(object):
            pass

        expected_msg = "User-defined rule class 'MyRuleClass' must extend from gitlint.rules.LineRule " + \
                       "or gitlint.rules.CommitRule"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_id(self):
        class MyRuleClass(rules.LineRule):
            pass

        # Rule class must have an id
        expected_msg = "User-defined rule class 'MyRuleClass' must have an 'id' attribute"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # Rule ids must be non-empty
        MyRuleClass.id = ""
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # Rule ids must not start with one of the reserved id letters
        for letter in ["T", "R", "B", "M"]:
            MyRuleClass.id = letter + "1"
            expected_msg = "The id '{0}' of 'MyRuleClass' is invalid. Gitlint reserves ids starting with R,T,B,M"
            with self.assertRaisesRegex(UserRuleError, expected_msg.format(letter)):
                assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_name(self):
        class MyRuleClass(rules.LineRule):
            id = "UC1"

        # Rule class must have an name
        expected_msg = "User-defined rule class 'MyRuleClass' must have a 'name' attribute"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # Rule names must be non-empty
        MyRuleClass.name = ""
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_option_spec(self):
        class MyRuleClass(rules.LineRule):
            id = "UC1"
            name = u"my-rüle-class"

        # if set, option_spec must be a list of gitlint options
        MyRuleClass.options_spec = u"föo"
        expected_msg = "The options_spec attribute of user-defined rule class 'MyRuleClass' must be a list " + \
                       "of gitlint.options.RuleOption"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # option_spec is a list, but not of gitlint options
        MyRuleClass.options_spec = [u"föo", 123]  # pylint: disable=bad-option-value,redefined-variable-type
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_validate(self):
        class MyRuleClass(rules.LineRule):
            id = "UC1"
            name = u"my-rüle-class"

        with self.assertRaisesRegex(UserRuleError,
                                    "User-defined rule class 'MyRuleClass' must have a 'validate' method"):
            assert_valid_rule_class(MyRuleClass)

        # validate attribute - not a method
        MyRuleClass.validate = u"föo"
        with self.assertRaisesRegex(UserRuleError,
                                    "User-defined rule class 'MyRuleClass' must have a 'validate' method"):
            assert_valid_rule_class(MyRuleClass)

    def test_assert_valid_rule_class_negative_target(self):
        class MyRuleClass(rules.LineRule):
            id = "UC1"
            name = u"my-rüle-class"

            def validate(self):
                pass

        # no target
        expected_msg = "The target attribute of the user-defined LineRule class 'MyRuleClass' must be either " + \
                       "gitlint.rules.CommitMessageTitle or gitlint.rules.CommitMessageBody"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # invalid target
        MyRuleClass.target = u"föo"
        with self.assertRaisesRegex(UserRuleError, expected_msg):
            assert_valid_rule_class(MyRuleClass)

        # valid target, no exception should be raised
        MyRuleClass.target = rules.CommitMessageTitle  # pylint: disable=bad-option-value,redefined-variable-type
        self.assertIsNone(assert_valid_rule_class(MyRuleClass))
