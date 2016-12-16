import os

from unittest2 import TestCase
from gitlint.git import GitContext


class BaseTestCase(TestCase):
    # In case of assert failures, print the full error message
    maxDiff = None

    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")

    @staticmethod
    def get_sample_path(filename=""):
        return os.path.join(BaseTestCase.SAMPLES_DIR, filename)

    @staticmethod
    def get_sample(filename=""):
        sample_path = BaseTestCase.get_sample_path(filename)
        sample = open(sample_path).read()
        return sample

    @staticmethod
    def get_expected(filename="", variable_dict=None):
        """ Utility method to read an 'expected' file and return it as a string. Optionally replace template variables
        specified by variable_dict. """
        expected_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
        expected_path = os.path.join(expected_dir, filename)
        expected = open(expected_path).read()
        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected

    @staticmethod
    def get_rule_rules_path():
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
