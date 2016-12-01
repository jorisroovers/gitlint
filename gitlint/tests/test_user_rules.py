import sys

from gitlint.tests.base import BaseTestCase
from gitlint.user_rules import find_rule_classes, assert_valid_rule_class, UserRuleError

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
        self.assertEqual(classes[0].id, "TUC1")
        self.assertEqual(classes[0].name, "my-user-commit-rule")
        expected_option = options.IntOption('violation-count', 0, "Number of violations to return")
        self.assertListEqual(classes[0].options_spec, [expected_option])
        self.assertTrue(hasattr(classes[0], "validate"))

        # Test that we can instantiate the class and can execute run the validate method and that it returns the
        # expected result
        rule_class = classes[0]()
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [])

        # Have it return a violation
        rule_class.options['violation-count'].value = 1
        violations = rule_class.validate("false-commit-object (ignored)")
        self.assertListEqual(violations, [rules.RuleViolation("TUC1", "Commit violation 1", "Content 1", 1)])

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
        with self.assertRaisesRegexp(UserRuleError, expected_msg):
            find_rule_classes(user_rule_path)

    def test_find_rule_classes_nonexisting_path(self):
        # When searching an non-existing path, we expect an OSError. That's fine because this case will be caught by
        # the CLI (you cannot specify a non-existing directory). What we do here is just assert that we indeed
        # get an OSError (so we guard against regressions).
        with self.assertRaisesRegexp(OSError, "No such file or directory"):
            find_rule_classes("foo/bar")

    def test_assert_valid_rule_class(self):
        class MyRuleClass(rules.Rule):
            pass

        self.assertTrue(assert_valid_rule_class(MyRuleClass))

    def test_assert_valid_rule_class_negative(self):
        class MyNormalClass(object):
            pass

        self.assertFalse(assert_valid_rule_class(MyNormalClass))
