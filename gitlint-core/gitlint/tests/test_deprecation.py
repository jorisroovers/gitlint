from gitlint.config import LintConfig
from gitlint.deprecation import Deprecation
from gitlint.rules import IgnoreByTitle
from gitlint.tests.base import EXPECTED_REGEX_STYLE_SEARCH_DEPRECATION_WARNING, BaseTestCase


class DeprecationTests(BaseTestCase):
    def test_get_regex_method(self):
        config = LintConfig()
        Deprecation.config = config
        rule = IgnoreByTitle({"regex": "^Releäse(.*)"})

        # When general.regex-style-search=True, we expect regex.search to be returned and no warning to be logged
        config.regex_style_search = True
        regex_method = Deprecation.get_regex_method(rule, rule.options["regex"])
        self.assertEqual(regex_method, rule.options["regex"].value.search)
        self.assert_logged([])

        # When general.regex-style-search=False, we expect regex.match to be returned and a warning to be logged
        config.regex_style_search = False
        regex_method = Deprecation.get_regex_method(rule, rule.options["regex"])
        self.assertEqual(regex_method, rule.options["regex"].value.match)
        self.assert_logged([EXPECTED_REGEX_STYLE_SEARCH_DEPRECATION_WARNING.format("I1", "ignore-by-title")])
