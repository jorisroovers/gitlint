# -*- coding: utf-8 -*-

from collections import OrderedDict
from gitlint import rules
from gitlint.config import RuleCollection
from gitlint.tests.base import BaseTestCase


class RuleCollectionTests(BaseTestCase):

    def test_add_rule(self):
        collection = RuleCollection()
        collection.add_rule(rules.TitleMaxLength, u"my-rüle", {"my_attr": u"föo", "my_attr2": 123})

        expected = rules.TitleMaxLength()
        expected.id = u"my-rüle"
        expected.my_attr = u"föo"
        expected.my_attr2 = 123

        self.assertEqual(len(collection), 1)
        self.assertDictEqual(collection._rules, OrderedDict({u"my-rüle": expected}))
        # Need to explicitely compare expected attributes as the rule.__eq__ method does not compare these attributes
        self.assertEqual(collection._rules[expected.id].my_attr, expected.my_attr)
        self.assertEqual(collection._rules[expected.id].my_attr2, expected.my_attr2)

    def test_add_find_rule(self):
        collection = RuleCollection()
        collection.add_rules([rules.TitleMaxLength, rules.TitleTrailingWhitespace], {"my_attr": u"föo"})

        # find by id
        expected = rules.TitleMaxLength()
        rule = collection.find_rule('T1')
        self.assertEqual(rule, expected)
        self.assertEqual(rule.my_attr, u"föo")

        # find by name
        expected2 = rules.TitleTrailingWhitespace()
        rule = collection.find_rule('title-trailing-whitespace')
        self.assertEqual(rule, expected2)
        self.assertEqual(rule.my_attr, u"föo")

        # find non-existing
        rule = collection.find_rule(u'föo')
        self.assertIsNone(rule)

    def test_delete_rules_by_attr(self):
        collection = RuleCollection()
        collection.add_rules([rules.TitleMaxLength, rules.TitleTrailingWhitespace], {"foo": u"bår"})
        collection.add_rules([rules.BodyHardTab], {"hur": u"dûr"})

        # Assert all rules are there as expected
        self.assertEqual(len(collection), 3)
        for expected_rule in [rules.TitleMaxLength(), rules.TitleTrailingWhitespace(), rules.BodyHardTab()]:
            self.assertEqual(collection.find_rule(expected_rule.id), expected_rule)

        # Delete rules by attr, assert that we still have the right rules in the collection
        collection.delete_rules_by_attr("foo", u"bår")
        self.assertEqual(len(collection), 1)
        self.assertIsNone(collection.find_rule(rules.TitleMaxLength.id), None)
        self.assertIsNone(collection.find_rule(rules.TitleTrailingWhitespace.id), None)

        found = collection.find_rule(rules.BodyHardTab.id)
        self.assertEqual(found, rules.BodyHardTab())
        self.assertEqual(found.hur, u"dûr")
