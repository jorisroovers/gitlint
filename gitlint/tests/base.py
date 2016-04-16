import os

from unittest2 import TestCase
from gitlint.git import GitContext


class BaseTestCase(TestCase):
    # In case of assert failures, print the full error message
    maxDiff = None

    @staticmethod
    def get_sample_path(filename=""):
        samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
        return os.path.join(samples_dir, filename)

    @staticmethod
    def get_sample(filename=""):
        sample_path = BaseTestCase.get_sample_path(filename)
        sample = open(sample_path).read()
        return sample

    @staticmethod
    def gitcontext(commit_msg_str, changed_files=None):
        """ Utility method to easily create gitcontext objects based on a given commit msg string and set of
        changed files"""
        gitcontext = GitContext.from_commit_msg(commit_msg_str)
        commit = gitcontext.commits[-1]
        if changed_files:
            commit.changed_files = changed_files
        return gitcontext
