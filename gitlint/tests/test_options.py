# -*- coding: utf-8 -*-
import os
import re

from gitlint.tests.base import BaseTestCase

from gitlint.options import IntOption, BoolOption, StrOption, ListOption, PathOption, RegexOption, RuleOptionError


class RuleOptionTests(BaseTestCase):
    def test_option_equality(self):
        options = {IntOption: 123, StrOption: "foöbar", BoolOption: False, ListOption: ["a", "b"],
                   PathOption: ".", RegexOption: "^foöbar(.*)"}
        for clazz, val in options.items():
            # 2 options are equal if their name, value and description match
            option1 = clazz("test-öption", val, "Test Dëscription")
            option2 = clazz("test-öption", val, "Test Dëscription")
            self.assertEqual(option1, option2)

        # Not equal: class, name, description, value are different
        self.assertNotEqual(option1, IntOption("tëst-option1", 123, "Test Dëscription"))
        self.assertNotEqual(option1, StrOption("tëst-option1", "åbc", "Test Dëscription"))
        self.assertNotEqual(option1, StrOption("tëst-option", "åbcd", "Test Dëscription"))
        self.assertNotEqual(option1, StrOption("tëst-option", "åbc", "Test Dëscription2"))

    def test_int_option(self):
        # normal behavior
        option = IntOption("tëst-name", 123, "Tëst Description")
        self.assertEqual(option.name, "tëst-name")
        self.assertEqual(option.description, "Tëst Description")
        self.assertEqual(option.value, 123)

        # re-set value
        option.set(456)
        self.assertEqual(option.value, 456)

        # set to None
        option.set(None)
        self.assertEqual(option.value, None)

        # error on negative int when not allowed
        expected_error = "Option 'tëst-name' must be a positive integer (current value: '-123')"
        with self.assertRaisesMessage(RuleOptionError, expected_error):
            option.set(-123)

        # error on non-int value
        expected_error = "Option 'tëst-name' must be a positive integer (current value: 'foo')"
        with self.assertRaisesMessage(RuleOptionError, expected_error):
            option.set("foo")

        # no error on negative value when allowed and negative int is passed
        option = IntOption("test-name", 123, "Test Description", allow_negative=True)
        option.set(-456)
        self.assertEqual(option.value, -456)

        # error on non-int value when negative int is allowed
        expected_error = "Option 'test-name' must be an integer (current value: 'foo')"
        with self.assertRaisesMessage(RuleOptionError, expected_error):
            option.set("foo")

    def test_str_option(self):
        # normal behavior
        option = StrOption("tëst-name", "föo", "Tëst Description")
        self.assertEqual(option.name, "tëst-name")
        self.assertEqual(option.description, "Tëst Description")
        self.assertEqual(option.value, "föo")

        # re-set value
        option.set("bår")
        self.assertEqual(option.value, "bår")

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
        option = BoolOption("tëst-name", "true", "Tëst Description")
        self.assertEqual(option.name, "tëst-name")
        self.assertEqual(option.description, "Tëst Description")
        self.assertEqual(option.value, True)

        # re-set value
        option.set("False")
        self.assertEqual(option.value, False)

        # Re-set using actual boolean
        option.set(True)
        self.assertEqual(option.value, True)

        # error on incorrect value
        incorrect_values = [1, -1, "foo", "bår", ["foo"], {'foo': "bar"}, None]
        for value in incorrect_values:
            with self.assertRaisesMessage(RuleOptionError, "Option 'tëst-name' must be either 'true' or 'false'"):
                option.set(value)

    def test_list_option(self):
        # normal behavior
        option = ListOption("tëst-name", "å,b,c,d", "Tëst Description")
        self.assertEqual(option.name, "tëst-name")
        self.assertEqual(option.description, "Tëst Description")
        self.assertListEqual(option.value, ["å", "b", "c", "d"])

        # re-set value
        option.set("1,2,3,4")
        self.assertListEqual(option.value, ["1", "2", "3", "4"])

        # set list
        option.set(["foo", "bår", "test"])
        self.assertListEqual(option.value, ["foo", "bår", "test"])

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
        option.set("ë,f,g,")
        self.assertListEqual(option.value, ["ë", "f", "g"])

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
        option = PathOption("tëst-directory", ".", "Tëst Description", type="dir")
        self.assertEqual(option.name, "tëst-directory")
        self.assertEqual(option.description, "Tëst Description")
        self.assertEqual(option.value, os.getcwd())
        self.assertEqual(option.type, "dir")

        # re-set value
        option.set(self.SAMPLES_DIR)
        self.assertEqual(option.value, self.SAMPLES_DIR)

        # set to None
        option.set(None)
        self.assertIsNone(option.value)

        # set to int
        expected = "Option tëst-directory must be an existing directory (current value: '1234')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(1234)

        # set to non-existing directory
        non_existing_path = os.path.join("/föo", "bar")
        expected = f"Option tëst-directory must be an existing directory (current value: '{non_existing_path}')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(non_existing_path)

        # set to a file, should raise exception since option.type = dir
        sample_path = self.get_sample_path(os.path.join("commit_message", "sample1"))
        expected = f"Option tëst-directory must be an existing directory (current value: '{sample_path}')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(sample_path)

        # set option.type = file, file should now be accepted, directories not
        option.type = "file"
        option.set(sample_path)
        self.assertEqual(option.value, sample_path)
        expected = f"Option tëst-directory must be an existing file (current value: '{self.get_sample_path()}')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set(self.get_sample_path())

        # set option.type = both, files and directories should now be accepted
        option.type = "both"
        option.set(sample_path)
        self.assertEqual(option.value, sample_path)
        option.set(self.get_sample_path())
        self.assertEqual(option.value, self.get_sample_path())

        # Expect exception if path type is invalid
        option.type = 'föo'
        expected = "Option tëst-directory type must be one of: 'file', 'dir', 'both' (current: 'föo')"
        with self.assertRaisesMessage(RuleOptionError, expected):
            option.set("haha")

    def test_regex_option(self):
        # normal behavior
        option = RegexOption("tëst-regex", "^myrëgex(.*)foo$", "Tëst Regex Description")
        self.assertEqual(option.name, "tëst-regex")
        self.assertEqual(option.description, "Tëst Regex Description")
        self.assertEqual(option.value, re.compile("^myrëgex(.*)foo$", re.UNICODE))

        # re-set value
        option.set("[0-9]föbar.*")
        self.assertEqual(option.value, re.compile("[0-9]föbar.*", re.UNICODE))

        # set None
        option.set(None)
        self.assertIsNone(option.value)

        # error on invalid regex
        incorrect_values = ["foo(", 123, -1]
        for value in incorrect_values:
            with self.assertRaisesRegex(RuleOptionError, "Invalid regular expression"):
                option.set(value)
