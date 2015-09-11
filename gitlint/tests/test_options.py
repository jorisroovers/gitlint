from gitlint.tests.base import BaseTestCase

from gitlint.options import IntOption, RuleOptionError


class RuleOptionTests(BaseTestCase):
    def test_int_option(self):
        # normal behavior
        option = IntOption("test-name", 123, "Test Description")
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
