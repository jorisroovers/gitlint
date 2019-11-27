import io
import logging
import os
import re

try:
    # python 2.x
    import unittest2 as unittest
except ImportError:
    # python 3.x
    import unittest

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.git import GitContext
from gitlint.utils import ustr, LOG_FORMAT, DEFAULT_ENCODING


# unittest2's assertRaisesRegex doesn't do unicode comparison.
# Let's monkeypatch the str() function to point to unicode() so that it does :)
# For reference, this is where this patch is required:
# https://hg.python.org/unittest2/file/tip/unittest2/case.py#l227
try:
    # python 2.x
    unittest.case.str = unicode
except (AttributeError, NameError):
    pass  # python 3.x


class BaseTestCase(unittest.TestCase):
    """ Base class of which all gitlint unit test classes are derived. Provides a number of convenience methods. """

    # In case of assert failures, print the full error message
    maxDiff = None

    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
    EXPECTED_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
    GITLINT_USE_SH_LIB = os.environ.get("GITLINT_USE_SH_LIB", "[NOT SET]")

    # List of 'git config' side-effects that can be used when mocking calls to git
    GIT_CONFIG_SIDE_EFFECTS = [
        u"#"  # git config --get core.commentchar
    ]

    def setUp(self):
        self.logcapture = LogCapture()
        self.logcapture.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger('gitlint').setLevel(logging.DEBUG)
        logging.getLogger('gitlint').handlers = [self.logcapture]

        # Make sure we don't propagate anything to child loggers, we need to do this explicitely here
        # because if you run a specific test file like test_lint.py, we won't be calling the setupLogging() method
        # in gitlint.cli that normally takes care of this
        logging.getLogger('gitlint').propagate = False

    @staticmethod
    def get_sample_path(filename=""):
        # Don't join up empty files names because this will add a trailing slash
        if filename == "":
            return ustr(BaseTestCase.SAMPLES_DIR)

        return ustr(os.path.join(BaseTestCase.SAMPLES_DIR, filename))

    @staticmethod
    def get_sample(filename=""):
        """ Read and return the contents of a file in gitlint/tests/samples """
        sample_path = BaseTestCase.get_sample_path(filename)
        with io.open(sample_path, encoding=DEFAULT_ENCODING) as content:
            sample = ustr(content.read())
        return sample

    @staticmethod
    def get_expected(filename="", variable_dict=None):
        """ Utility method to read an expected file from gitlint/tests/expected and return it as a string.
        Optionally replace template variables specified by variable_dict. """
        expected_path = os.path.join(BaseTestCase.EXPECTED_DIR, filename)
        with io.open(expected_path, encoding=DEFAULT_ENCODING) as content:
            expected = ustr(content.read())

        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected

    @staticmethod
    def get_user_rules_path():
        return os.path.join(BaseTestCase.SAMPLES_DIR, "user_rules")

    @staticmethod
    def gitcontext(commit_msg_str, changed_files=None, ):
        """ Utility method to easily create gitcontext objects based on a given commit msg string and an optional set of
        changed files"""
        with patch("gitlint.git.git_commentchar") as comment_char:
            comment_char.return_value = u"#"
            gitcontext = GitContext.from_commit_msg(commit_msg_str)
            commit = gitcontext.commits[-1]
            if changed_files:
                commit.changed_files = changed_files
            return gitcontext

    @staticmethod
    def gitcommit(commit_msg_str, changed_files=None, **kwargs):
        """ Utility method to easily create git commit given a commit msg string and an optional set of changed files"""
        gitcontext = BaseTestCase.gitcontext(commit_msg_str, changed_files)
        commit = gitcontext.commits[-1]
        for attr, value in kwargs.items():
            setattr(commit, attr, value)
        return commit

    def assert_logged(self, expected):
        """ Asserts that the logs match an expected string or list.
            This method knows how to compare a passed list of log lines as well as a newline concatenated string
            of all loglines. """
        if isinstance(expected, list):
            self.assertListEqual(self.logcapture.messages, expected)
        else:
            self.assertEqual("\n".join(self.logcapture.messages), expected)

    def assert_log_contains(self, line):
        """ Asserts that a certain line is in the logs """
        self.assertIn(line, self.logcapture.messages)

    def assertRaisesRegex(self, expected_exception, expected_regex, *args, **kwargs):
        """ Pass-through method to unittest.TestCase.assertRaisesRegex that applies re.escape() to the passed
            `expected_regex`. This is useful to automatically escape all file paths that might be present in the regex.
        """
        return super(BaseTestCase, self).assertRaisesRegex(expected_exception, re.escape(expected_regex),
                                                           *args, **kwargs)


class LogCapture(logging.Handler):
    """ Mock logging handler used to capture any log messages during tests."""

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.messages = []

    def emit(self, record):
        self.messages.append(ustr(self.format(record)))
