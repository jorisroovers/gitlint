import os
import unittest2

from gitlint.git import GitContext
from gitlint.utils import ustr

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

    @staticmethod
    def get_sample_path(filename=""):
        return os.path.join(BaseTestCase.SAMPLES_DIR, filename)

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
    def gitcommit(commit_msg_str, changed_files=None):
        """ Utility method to easily create git commit given a commit msg string and an optional set of changed files"""
        gitcontext = BaseTestCase.gitcontext(commit_msg_str, changed_files)
        return gitcontext.commits[-1]
