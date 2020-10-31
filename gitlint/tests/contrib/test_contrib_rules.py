# -*- coding: utf-8 -*-
import os

from gitlint.tests.base import BaseTestCase
from gitlint.contrib import rules as contrib_rules
from gitlint.tests.contrib import rules as contrib_tests
from gitlint import rule_finder, rules


class ContribRuleTests(BaseTestCase):

    CONTRIB_DIR = os.path.dirname(os.path.realpath(contrib_rules.__file__))

    def test_contrib_tests_exist(self):
        """ Tests that every contrib rule file has an associated test file.
            While this doesn't guarantee that every contrib rule has associated tests (as we don't check the content
            of the tests file), it's a good leading indicator. """

        contrib_tests_dir = os.path.dirname(os.path.realpath(contrib_tests.__file__))
        contrib_test_files = os.listdir(contrib_tests_dir)

        # Find all python files in the contrib dir and assert there's a corresponding test file
        for filename in os.listdir(self.CONTRIB_DIR):
            if filename.endswith(".py") and filename not in ["__init__.py"]:
                expected_test_file = "test_" + filename
                error_msg = "Every Contrib Rule must have associated tests. " + \
                            f"Expected test file {os.path.join(contrib_tests_dir, expected_test_file)} not found."
                self.assertIn(expected_test_file, contrib_test_files, error_msg)

    def test_contrib_rule_naming_conventions(self):
        """ Tests that contrib rules follow certain naming conventions.
            We can test for this at test time (and not during runtime like rule_finder.assert_valid_rule_class does)
            because these are contrib rules: once they're part of gitlint they can't change unless they pass this test
            again.
        """
        rule_classes = rule_finder.find_rule_classes(self.CONTRIB_DIR)

        for clazz in rule_classes:
            # Contrib rule names start with "contrib-"
            self.assertTrue(clazz.name.startswith("contrib-"))

            # Contrib line rules id's start with "CL"
            if issubclass(clazz, rules.LineRule):
                if clazz.target == rules.CommitMessageTitle:
                    self.assertTrue(clazz.id.startswith("CT"))
                elif clazz.target == rules.CommitMessageBody:
                    self.assertTrue(clazz.id.startswith("CB"))

    def test_contrib_rule_uniqueness(self):
        """ Tests that all contrib rules have unique identifiers.
            We can test for this at test time (and not during runtime like rule_finder.assert_valid_rule_class does)
            because these are contrib rules: once they're part of gitlint they can't change unless they pass this test
            again.
        """
        rule_classes = rule_finder.find_rule_classes(self.CONTRIB_DIR)

        # Not very efficient way of checking uniqueness, but it works :-)
        class_names = [rule_class.name for rule_class in rule_classes]
        class_ids = [rule_class.id for rule_class in rule_classes]
        self.assertEqual(len(set(class_names)), len(class_names))
        self.assertEqual(len(set(class_ids)), len(class_ids))

    def test_contrib_rule_instantiated(self):
        """ Tests that all contrib rules can be instantiated without errors. """
        rule_classes = rule_finder.find_rule_classes(self.CONTRIB_DIR)

        # No exceptions = what we want :-)
        for rule_class in rule_classes:
            rule_class()
