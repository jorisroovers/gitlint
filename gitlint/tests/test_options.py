# -*- coding: utf-8 -*-
import os
import re

from gitlint.tests.base import BaseTestCase

from gitlint.options import IntOption, BoolOption, StrOption, ListOption, PathOption, RegexOption, RuleOptionError


class RuleOptionTests(BaseTestCase):
    def test_option_equality(self):
        options = {IntOption: 123, StrOption: u"foöbar", BoolOption: False, ListOption: ["a", "b"],
                   PathOption: ".", RegexOption: u"^foöbar(.*)"}
        for clazz, val in options.items():
            # 2 options are equal if their name, value and description match
            option1 = clazz(u"test-öption", val, u"Test Dëscription")
            option2 = clazz(u"test-öption", val, u"Test Dëscription")
            self.assertEqual(option1, option2)

        # Not equal: class, name, description, value are different
        self.assertNotEqual(option1, IntOption(u"tëst-option1", 123, u"Test Dëscription"))
        self.assertNotEqual(option1, StrOption(u"tëst-option1", u"åbc", u"Test Dëscription"))
        self.assertNotEqual(option1, StrOption(u"tëst-option", u"åbcd", u"Test Dëscription"))
        self.assertNotEqual(option1, StrOption(u"tëst-option", u"åbc", u"Test Dëscription2"))

    def test_int_option(self):
        # normal behavior
        option = IntOption(u"tëst-name", 123, u"Tëst Description")
        self.assertEqual(option.name, u"tëst-name")
        self.assertEqual(option.description, u"Tëst Description")
        self.assertEqual(option.value, 123)

        # re-set value
        option.set(456)
        self.assertEqual(option.value, 456)

        # set to None
        option.set(None)
        self.assertEqual(option.value, None)

        # error on negative int when not allowed
        expected_error = u"Option 'tëst-name' must be a positive integer (current value: '-123')"
        with self.assertRaisesMessage(RuleOptionError, expected_error):
            option.set(-123)

        # error on non-int value
        expected_error = u"Option 'tëst-name' must be a positive integer (current value: 'foo')"
        with self.assertRaisesMessage(RuleOptionError, expected_error):
            option.set("foo")

        # no error on negative value when allowed and negative int is passed
        option = IntOption("test-name", 123, "Test Description", allow_negative=True)
        option.set(-456)
        self.assertEqual(option.value, -456)

        # error on non-int value when negative int is allowed
        expected_error = u"Option 'test-name' must be an integer (current value: 'foo')"
        with self.assertRaisesMessage(RuleOptionError, expected_error):
            option.set("foo")

    def test_str_option(self):
        # normal behavior
        option = StrOption(u"tëst-name", u"föo", u"Tëst Description")
        self.assertEqual(option.name, u"tëst-name")
        self.assertEqual(option.description, u"Tëst Description")
        self.assertEqual(option.value, u"föo")

        # re-set value
        option.set(u"bår")
        self.assertEqual(option.value, u"bår")

        # conversion to str
        option.set(123)
        self.assertEqual(option.value, "123")

        # conversion to str
        option.set(-123)
        self.assertEqual(option.value, "-123")

        # None value
        option.set(None)
        self.assertEqual(option.value, None)

    def test_boolean_option(self):
        # normal behavior
        option = BoolOption(u"tëst-name", "true", u"Tëst Description")
        self.assertEqual(option.name, u"tëst-name")
        self.assertEqual(option.description, u"Tëst Description")
        self.assertEqual(option.value, True)

        # re-set value
        option.set("False")
        self.assertEqual(option.value, False)

        # Re-set using actual boolean
        option.set(True)
        self.assertEqual(option.value, True)

        # error on incorrect value
        incorrect_values = [1, -1, "foo", u"bår", ["foo"], {'foo': "bar"}, None]
        for value in incorrect_values:
            with self.assertRaisesMessage(RuleOptionError, u"Option 'tëst-name' must be either 'true' or 'false'"):
                option.set(value)

    def test_list_option(self):
        # normal behavior
        option = ListOption(u"tëst-name", u"å,b,c,d", u"Tëst Description")
        self.assertEqual(option.name, u"tëst-name")
        self.assertEqual(option.description, u"Tëst Description")
        self.assertListEqual(option.value, [u"å", u"b", u"c", u"d"])

        # re-set value
        option.set(u"1,2,3,4")
        self.assertListEqual(option.value, [u"1", u"2", u"3", u"4"])

        # set list
        option.set([u"foo", u"bår", u"test"])
        self.assertListEqual(option.value, [u"foo", u"bår", u"test"])

        # None
        option.set(None)
        self.assertIsNone(option.value)

        # empty string
        option.set("")
        self.assertListEqual(option.value, [])

        # whitespace string
        option.set("  \t  ")
        self.assertListEqual(option.value, [])

        # empty list
        option.set([])
        self.assertListEqual(option.value, [])

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

    def test_path_option(self):
        option = PathOption(u"tëst-directory", ".", u"Tëst Description", type=u"dir")
        self.assertEqual(option.name, u"tëst-directory")
        self.assertEqual(option.description, u"Tëst Description")
        self.assertEqual(option.value, os.getcwd())
        self.assertEqual(option.type, u"dir")

        # re-set value
        option.set(self.SAMPLES_DIR)
        self.assertEqual(option.value, self.SAMPLES_DIR)

        # set to None
        option.set(None)
        self.assertIsNone(option.value)

        # set to int
        expected = u"Option tëst-directory must be an existing directory (current value: '1234')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(1234)

        # set to non-existing directory
        non_existing_path = os.path.join(u"/föo", u"bar")
        expected = u"Option tëst-directory must be an existing directory (current value: '{0}')"
        with self.assertRaisesMessage(RuleOptionError, expected.format(non_existing_path)):
            option.set(non_existing_path)

        # set to a file, should raise exception since option.type = dir
        sample_path = self.get_sample_path(os.path.join("commit_message", "sample1"))
        expected = u"Option tëst-directory must be an existing directory (current value: '{0}')".format(sample_path)
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(sample_path)

        # set option.type = file, file should now be accepted, directories not
        option.type = u"file"
        option.set(sample_path)
        self.assertEqual(option.value, sample_path)
        expected = u"Option tëst-directory must be an existing file (current value: '{0}')".format(
            self.get_sample_path())
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(self.get_sample_path())

        # set option.type = both, files and directories should now be accepted
        option.type = u"both"
        option.set(sample_path)
        self.assertEqual(option.value, sample_path)
        option.set(self.get_sample_path())
        self.assertEqual(option.value, self.get_sample_path())

        # Expect exception if path type is invalid
        option.type = u'föo'
        expected = u"Option tëst-directory type must be one of: 'file', 'dir', 'both' (current: 'föo')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set("haha")

    def test_regex_option(self):
        # normal behavior
        option = RegexOption(u"tëst-regex", u"^myrëgex(.*)foo$", u"Tëst Regex Description")
        self.assertEqual(option.name, u"tëst-regex")
        self.assertEqual(option.description, u"Tëst Regex Description")
        self.assertEqual(option.value, re.compile(u"^myrëgex(.*)foo$", re.UNICODE))

        # re-set value
        option.set(u"[0-9]föbar.*")
        self.assertEqual(option.value, re.compile(u"[0-9]föbar.*", re.UNICODE))

        # set None
        option.set(None)
        self.assertIsNone(option.value)

        # error on invalid regex
        incorrect_values = [u"foo(", 123, -1]
        for value in incorrect_values:
            with self.assertRaisesRegex(RuleOptionError, u"Invalid regular expression"):
                option.set(value)
