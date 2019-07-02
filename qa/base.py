# -*- coding: utf-8 -*-
# pylint: disable=bad-option-value,unidiomatic-typecheck,undefined-variable,no-else-return,
# pylint: disable=too-many-function-args,unexpected-keyword-arg

import io
import os
import sys
import tempfile
from datetime import datetime
from uuid import uuid4

try:
    # python 2.x
    from unittest2 import TestCase
except ImportError:
    # python 3.x
    from unittest import TestCase

import sh
from sh import git, rm, touch, RunningCommand  # pylint: disable=no-name-in-module

DEFAULT_ENCODING = sh.DEFAULT_ENCODING


def ustr(obj):
    """ Python 2 and 3 utility method that converts an obj to unicode in python 2 and to a str object in python 3"""
    if sys.version_info[0] == 2:
        # If we are getting a string, then do an explicit decode
        # else, just call the unicode method of the object
        if type(obj) in [str, basestring]:  # pragma: no cover # noqa
            return unicode(obj, DEFAULT_ENCODING)  # pragma: no cover # noqa
        else:
            return unicode(obj)  # pragma: no cover # noqa
    else:
        if type(obj) in [bytes]:
            return obj.decode(DEFAULT_ENCODING)
        else:
            return str(obj)


class BaseTestCase(TestCase):
    """ Base class of which all gitlint integration test classes are derived.
        Provides a number of convenience methods. """

    # In case of assert failures, print the full error message
    maxDiff = None
    tmp_git_repo = None

    GITLINT_USE_SH_LIB = os.environ.get("GITLINT_USE_SH_LIB", "[NOT SET]")

    def setUp(self):
        self.tmpfiles = []

    def tearDown(self):
        for tmpfile in self.tmpfiles:
            os.remove(tmpfile)

    def assertEqualStdout(self, output, expected):  # pylint: disable=invalid-name
        self.assertIsInstance(output, RunningCommand)
        output = output.stdout.decode(DEFAULT_ENCODING)
        output = output.replace('\r\n', '\n')
        self.assertMultiLineEqual(output, expected)

    @classmethod
    def setUpClass(cls):
        """ Sets up the integration tests by creating a new temporary git repository """
        cls.tmp_git_repos = []
        cls.tmp_git_repo = cls.create_tmp_git_repo()

    @classmethod
    def tearDownClass(cls):
        """ Cleans up the temporary git repositories """
        for repo in cls.tmp_git_repos:
            rm("-rf", repo)

    @classmethod
    def generate_temp_path(cls):
        return os.path.realpath("/tmp/gitlint-test-{0}".format(datetime.now().strftime("%Y%m%d-%H%M%S-%f")))

    @classmethod
    def create_tmp_git_repo(cls):
        """ Creates a temporary git repository and returns its directory path """
        tmp_git_repo = cls.generate_temp_path()
        cls.tmp_git_repos.append(tmp_git_repo)

        git("init", tmp_git_repo)
        # configuring name and email is required in every git repot
        git("config", "user.name", "gitlint-test-user", _cwd=tmp_git_repo)
        git("config", "user.email", "gitlint@test.com", _cwd=tmp_git_repo)

        # Git does not by default print unicode paths, fix that by setting core.quotePath to false
        # http://stackoverflow.com/questions/34549040/git-not-displaying-unicode-file-names
        # ftp://www.kernel.org/pub/software/scm/git/docs/git-config.html
        git("config", "core.quotePath", "false", _cwd=tmp_git_repo)

        # Git on mac doesn't like unicode characters by default, so we need to set this option
        # http://stackoverflow.com/questions/5581857/git-and-the-umlaut-problem-on-mac-os-x
        git("config", "core.precomposeunicode", "true", _cwd=tmp_git_repo)

        return tmp_git_repo

    def _create_simple_commit(self, message, out=None, ok_code=None, env=None, git_repo=None, tty_in=False):
        """ Creates a simple commit with an empty test file.
            :param message: Commit message for the commit. """

        git_repo = self.tmp_git_repo if git_repo is None else git_repo

        # Let's make sure that we copy the environment in which this python code was executed as environment
        # variables can influence how git runs.
        # This was needed to fix https://github.com/jorisroovers/gitlint/issues/15 as we need to make sure to use
        # the PATH variable that contains the virtualenv's python binary.
        environment = os.environ
        if env:
            environment.update(env)

        test_filename = u"test-fïle-" + str(uuid4())
        touch(test_filename, _cwd=git_repo)
        git("add", test_filename, _cwd=git_repo)
        # https://amoffat.github.io/sh/#interactive-callbacks
        if not ok_code:
            ok_code = [0]

        git("commit", "-m", message, _cwd=git_repo, _err_to_out=True, _out=out, _tty_in=tty_in,
            _ok_code=ok_code, _env=environment)
        return test_filename

    def create_tmpfile(self, content):
        """ Utility method to create temp files. These are cleaned at the end of the test """
        # Not using a context manager to avoid unneccessary identation in test code
        tmpfile, tmpfilepath = tempfile.mkstemp()
        self.tmpfiles.append(tmpfilepath)
        with os.fdopen(tmpfile, "w") as f:
            f.write(content)
        return tmpfilepath

    @staticmethod
    def get_example_path(filename=""):
        examples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../examples")
        return os.path.join(examples_dir, filename)

    @staticmethod
    def get_sample_path(filename=""):
        samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
        return os.path.join(samples_dir, filename)

    def get_last_commit_short_hash(self, git_repo=None):
        git_repo = self.tmp_git_repo if git_repo is None else git_repo
        return git("rev-parse", "--short", "HEAD", _cwd=git_repo, _err_to_out=True).replace("\n", "")

    def get_last_commit_hash(self, git_repo=None):
        git_repo = self.tmp_git_repo if git_repo is None else git_repo
        return git("rev-parse", "HEAD", _cwd=git_repo, _err_to_out=True).replace("\n", "")

    @staticmethod
    def get_expected(filename="", variable_dict=None):
        """ Utility method to read an 'expected' file and return it as a string. Optionally replace template variables
        specified by variable_dict. """
        expected_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
        expected_path = os.path.join(expected_dir, filename)
        expected = io.open(expected_path, encoding=DEFAULT_ENCODING).read()

        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected
