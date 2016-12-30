# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from uuid import uuid4

from unittest2 import TestCase
from sh import git, rm, touch, DEFAULT_ENCODING  # pylint: disable=no-name-in-module


class BaseTestCase(TestCase):
    """ Base class of which all gitlint integration test classes are derived.
        Provides a number of convenience methods. """

    # In case of assert failures, print the full error message
    maxDiff = None
    tmp_git_repo = None

    @classmethod
    def setUpClass(cls):
        """ Sets up the integration tests by creating a new temporary git repository """
        cls.tmp_git_repo = os.path.realpath("/tmp/gitlint-test-%s" % datetime.now().strftime("%Y%m%d-%H%M%S"))
        git("init", cls.tmp_git_repo)
        # configuring name and email is required in every git repot
        git("config", "user.name", "gitlint-test-user", _cwd=cls.tmp_git_repo)
        git("config", "user.email", "gitlint@test.com", _cwd=cls.tmp_git_repo)

        # Git does not by default print unicode paths, fix that by setting core.quotePath to false
        # http://stackoverflow.com/questions/34549040/git-not-displaying-unicode-file-names
        # ftp://www.kernel.org/pub/software/scm/git/docs/git-config.html
        git("config", "core.quotePath", "false", _cwd=cls.tmp_git_repo)

    @classmethod
    def tearDownClass(cls):
        """ Cleans up the temporary git repository """
        rm("-rf", cls.tmp_git_repo)

    def _create_simple_commit(self, message, out=None, ok_code=None, env=None):
        """ Creates a simple commit with an empty test file.
            :param message: Commit message for the commit. """

        # Let's make sure that we copy the environment in which this python code was executed as environment
        # variables can influence how git runs.
        # This was needed to fix https://github.com/jorisroovers/gitlint/issues/15 as we need to make sure to use
        # the PATH variable that contains the virtualenv's python binary.
        environment = os.environ
        if env:
            environment.update(env)

        test_filename = u"test-fïle-" + str(uuid4())
        touch(test_filename, _cwd=self.tmp_git_repo)
        git("add", test_filename, _cwd=self.tmp_git_repo)
        # https://amoffat.github.io/sh/#interactive-callbacks
        if not ok_code:
            ok_code = [0]

        git("commit", "-m", message, _cwd=self.tmp_git_repo, _tty_in=True, _out=out, _ok_code=ok_code, _env=environment)
        return test_filename

    @staticmethod
    def get_example_path(filename=""):
        examples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../examples")
        return os.path.join(examples_dir, filename)

    @staticmethod
    def get_sample_path(filename=""):
        samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
        return os.path.join(samples_dir, filename)

    @staticmethod
    def get_expected(filename="", variable_dict=None):
        """ Utility method to read an 'expected' file and return it as a string. Optionally replace template variables
        specified by variable_dict. """
        expected_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
        expected_path = os.path.join(expected_dir, filename)
        expected = open(expected_path).read()
        if sys.version_info[0] == 2:  # decode string if python2
            expected = unicode(expected, DEFAULT_ENCODING)  # noqa # pylint: disable=undefined-variable

        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected
