from gitlint.tests.base import BaseTestCase

from gitlint.options import IntOption, BoolOption, StrOption, ListOption, RuleOptionError


class RuleOptionTests(BaseTestCase):
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
        expected_error = "Option 'test-name' must be a positive integer \(current value: '-123'\)"
        with self.assertRaisesRegexp(RuleOptionError, expected_error):
            option.set(-123)

        # error on non-int value
        expected_error = "Option 'test-name' must be a positive integer \(current value: 'foo'\)"
        with self.assertRaisesRegexp(RuleOptionError, expected_error):
            option.set("foo")

        # no error on negative value when allowed and negative int is passed
        option = IntOption("test-name", 123, "Test Description", allow_negative=True)
        option.set(-456)
        self.assertEqual(option.value, -456)

        # error on non-int value when negative int is allowed
        expected_error = "Option 'test-name' must be an integer \(current value: 'foo'\)"
        with self.assertRaisesRegexp(RuleOptionError, expected_error):
            option.set("foo")

    def test_str_option(self):
        # normal behavior
        option = StrOption("test-name", "foo", "Test Description")
        self.assertEqual(option.value, "foo")
        self.assertEqual(option.name, "test-name")
        self.assertEqual(option.description, "Test Description")

        # re-set value
        option.set("foo")
        self.assertEqual(option.value, "foo")

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
        expected_error = "Option 'test-name' must be either 'true' or 'false'"
        with self.assertRaisesRegexp(RuleOptionError, expected_error):
            option.set("foo")

    def test_list_option(self):
        # normal behavior
        option = ListOption("test-name", "a,b,c,d", "Test Description")
        self.assertListEqual(option.value, ["a", "b", "c", "d"])

        # re-set value
        option.set("1,2,3,4")
        self.assertListEqual(option.value, ["1", "2", "3", "4"])

        # set list
        option.set(["foo", "bar", "test"])
        self.assertListEqual(option.value, ["foo", "bar", "test"])

        # trailing comma
        option.set("e,f,g,")
        self.assertListEqual(option.value, ["e", "f", "g"])

        # spaces should be trimmed
        option.set(" abc , def   , ghi \t ")
        self.assertListEqual(option.value, ["abc", "def", "ghi"])

        # conversion to string before split
        option.set(123)
        self.assertListEqual(option.value, ["123"])
