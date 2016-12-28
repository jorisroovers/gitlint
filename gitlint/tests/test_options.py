# -*- coding: utf-8 -*-
import os

from gitlint.tests.base import BaseTestCase

from gitlint.options import IntOption, BoolOption, StrOption, ListOption, DirectoryOption, RuleOptionError


class RuleOptionTests(BaseTestCase):
    def test_option_equals(self):
        # 2 options are equal if their name, value and description match
        option1 = IntOption("test-option", 123, u"Test Dëscription")
        option2 = IntOption("test-option", 123, u"Test Dëscription")
        self.assertEqual(option1, option2)

        # Not equal: name, description, value are different
        self.assertNotEqual(option1, IntOption("test-option1", 123, u"Test Dëscription"))
        self.assertNotEqual(option1, IntOption("test-option", 1234, u"Test Dëscription"))
        self.assertNotEqual(option1, IntOption("test-option", 123, u"Test Dëscription2"))

    def test_int_option(self):
        # normal behavior
        option = IntOption("test-name", 123, "Test Description")
        self.assertEqual(option.value, 123)
        self.assertEqual(option.name, "test-name")
        self.assertEqual(option.description, "Test Description")

        # re-set value
        option.set(456)
        self.assertEqual(option.value, 456)

        # error on negative int when not allowed
        expected_error = r"Option 'test-name' must be a positive integer \(current value: '-123'\)"
        with self.assertRaisesRegex(RuleOptionError, expected_error):
            option.set(-123)

        # error on non-int value
        expected_error = r"Option 'test-name' must be a positive integer \(current value: 'foo'\)"
        with self.assertRaisesRegex(RuleOptionError, expected_error):
            option.set("foo")

        # no error on negative value when allowed and negative int is passed
        option = IntOption("test-name", 123, "Test Description", allow_negative=True)
        option.set(-456)
        self.assertEqual(option.value, -456)

        # error on non-int value when negative int is allowed
        expected_error = r"Option 'test-name' must be an integer \(current value: 'foo'\)"
        with self.assertRaisesRegex(RuleOptionError, expected_error):
            option.set("foo")

    def test_str_option(self):
        # normal behavior
        option = StrOption("test-name", u"föo", "Test Description")
        self.assertEqual(option.value, u"föo")
        self.assertEqual(option.name, "test-name")
        self.assertEqual(option.description, "Test Description")

        # re-set value
        option.set(u"bår")
        self.assertEqual(option.value, u"bår")

        # conversion to str
        option.set(123)
        self.assertEqual(option.value, "123")

        # conversion to str
        option.set(-123)
        self.assertEqual(option.value, "-123")

    def test_boolean_option(self):
        # normal behavior
        option = BoolOption("test-name", "true", "Test Description")
        self.assertEqual(option.value, True)

        # re-set value
        option.set("False")
        self.assertEqual(option.value, False)

        # Re-set using actual boolean
        option.set(True)
        self.assertEqual(option.value, True)

        # error on incorrect value
        incorrect_values = [1, -1, "foo", u"bår", ["foo"], {'foo': "bar"}]
        for value in incorrect_values:
            with self.assertRaisesRegex(RuleOptionError, "Option 'test-name' must be either 'true' or 'false'"):
                option.set(value)

    def test_list_option(self):
        # normal behavior
        option = ListOption("test-name", u"å,b,c,d", "Test Description")
        self.assertListEqual(option.value, [u"å", u"b", u"c", u"d"])

        # re-set value
        option.set(u"1,2,3,4")
        self.assertListEqual(option.value, [u"1", u"2", u"3", u"4"])

        # set list
        option.set([u"foo", u"bår", u"test"])
        self.assertListEqual(option.value, [u"foo", u"bår", u"test"])

        # trailing comma
        option.set(u"ë,f,g,")
        self.assertListEqual(option.value, [u"ë", u"f", u"g"])

        # leading and trailing whitespace should be trimmed, but only deduped within text
        option.set(" abc , def   , ghi \t  , jkl  mno  ")
        self.assertListEqual(option.value, ["abc", "def", "ghi", "jkl  mno"])

        # Also strip whitespace within a list
        option.set(["\t foo", "bar \t ", " test  123 "])
        self.assertListEqual(option.value, ["foo", "bar", "test  123"])

        # conversion to string before split
        option.set(123)
        self.assertListEqual(option.value, ["123"])

    def test_dir_option(self):
        option = DirectoryOption("test-directory", ".", u"Test Description")
        self.assertEqual(option.value, os.getcwd())
        self.assertEqual(option.name, "test-directory")
        self.assertEqual(option.description, u"Test Description")

        # re-set value
        option.set(self.SAMPLES_DIR)
        self.assertEqual(option.value, self.SAMPLES_DIR)

        # set to non-existing directory
        expected = u"Option test-directory must be an existing directory \(current value: '/föo/bar'\)"
        with self.assertRaisesRegex(RuleOptionError, expected):
            option.set(u"/föo/bar")

        # set to int
        expected = u"Option test-directory must be an existing directory \(current value: '1234'\)"
        with self.assertRaisesRegex(RuleOptionError, expected):
            option.set(1234)
