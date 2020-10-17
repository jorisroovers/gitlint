# -*- coding: utf-8 -*-

from gitlint import utils
from gitlint.tests.base import BaseTestCase

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error


class UtilsTests(BaseTestCase):

    def tearDown(self):
        # Since we're messing around with `utils.PLATFORM_IS_WINDOWS` during these tests, we need to reset
        # its value after we're done this doesn't influence other tests
        utils.PLATFORM_IS_WINDOWS = utils.platform_is_windows()

    @patch('os.environ')
    def test_use_sh_library(self, patched_env):
        patched_env.get.return_value = "1"
        self.assertEqual(utils.use_sh_library(), True)
        patched_env.get.assert_called_once_with("GITLINT_USE_SH_LIB", None)

        for invalid_val in ["0", u"foöbar"]:
            patched_env.get.reset_mock()  # reset mock call count
            patched_env.get.return_value = invalid_val
            self.assertEqual(utils.use_sh_library(), False, invalid_val)
            patched_env.get.assert_called_once_with("GITLINT_USE_SH_LIB", None)

        # Assert that when GITLINT_USE_SH_LIB is not set, we fallback to checking whether we're on Windows
        utils.PLATFORM_IS_WINDOWS = True
        patched_env.get.return_value = None
        self.assertEqual(utils.use_sh_library(), False)

        utils.PLATFORM_IS_WINDOWS = False
        self.assertEqual(utils.use_sh_library(), True)

    @patch('gitlint.utils.locale')
    def test_default_encoding_non_windows(self, mocked_locale):
        utils.PLATFORM_IS_WINDOWS = False
        mocked_locale.getpreferredencoding.return_value = u"foöbar"
        self.assertEqual(utils.getpreferredencoding(), u"foöbar")
        mocked_locale.getpreferredencoding.assert_called_once()

        mocked_locale.getpreferredencoding.return_value = False
        self.assertEqual(utils.getpreferredencoding(), u"UTF-8")

    @patch('os.environ')
    def test_default_encoding_windows(self, patched_env):
        utils.PLATFORM_IS_WINDOWS = True
        # Mock out os.environ
        mock_env = {}

        def mocked_get(key, default):
            return mock_env.get(key, default)

        patched_env.get.side_effect = mocked_get

        # Assert getpreferredencoding reads env vars in order: LC_ALL, LC_CTYPE, LANG
        mock_env = {"LC_ALL": u"ASCII", "LC_CTYPE": u"UTF-16", "LANG": u"CP1251"}
        self.assertEqual(utils.getpreferredencoding(), u"ASCII")
        mock_env = {"LC_CTYPE": u"UTF-16", "LANG": u"CP1251"}
        self.assertEqual(utils.getpreferredencoding(), u"UTF-16")
        mock_env = {"LANG": u"CP1251"}
        self.assertEqual(utils.getpreferredencoding(), u"CP1251")

        # Assert split on dot
        mock_env = {"LANG": u"foo.UTF-16"}
        self.assertEqual(utils.getpreferredencoding(), u"UTF-16")

        # assert default encoding is UTF-8
        mock_env = {}
        self.assertEqual(utils.getpreferredencoding(), "UTF-8")
        mock_env = {"FOO": u"föo"}
        self.assertEqual(utils.getpreferredencoding(), "UTF-8")

        # assert fallback encoding is UTF-8 in case we set an unavailable encoding
        mock_env = {"LC_ALL": u"foo"}
        self.assertEqual(utils.getpreferredencoding(), u"UTF-8")
