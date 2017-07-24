import logging
import os
import unittest2

from gitlint.git import GitContext
from gitlint.utils import ustr, LOG_FORMAT

# unittest2's assertRaisesRegex doesn't do unicode comparison.
# Let's monkeypatch the str() function to point to unicode() so that it does :)
# For reference, this is where this patch is required:
# https://hg.python.org/unittest2/file/tip/unittest2/case.py#l227
try:
    unittest2.case.str = unicode
except NameError:
    pass  # python 3


class BaseTestCase(unittest2.TestCase):
    """ Base class of which all gitlint unit test classes are derived. Provides a number of convenience methods. """

    # In case of assert failures, print the full error message
    maxDiff = None

    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")

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
        sample = ustr(open(sample_path).read())
        return sample

    @staticmethod
    def get_expected(filename="", variable_dict=None):
        """ Utility method to read an expected file from gitlint/tests/expected and return it as a string.
        Optionally replace template variables specified by variable_dict. """
        expected_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
        expected_path = os.path.join(expected_dir, filename)
        expected = ustr(open(expected_path).read())

        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected

    @staticmethod
    def get_user_rules_path():
        return os.path.join(BaseTestCase.SAMPLES_DIR, "user_rules")

    @staticmethod
    def gitcontext(commit_msg_str, changed_files=None):
        """ Utility method to easily create gitcontext objects based on a given commit msg string and an optional set of
        changed files"""
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

    def assert_logged(self, lines):
        """ Asserts that a certain list of messages has been logged """
        self.assertListEqual(self.logcapture.messages, lines)


class LogCapture(logging.Handler):
    """ Mock logging handler used to capture any log messages during tests."""

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.messages = []

    def emit(self, record):
        self.messages.append(ustr(self.format(record)))
