import os
from datetime import datetime
from uuid import uuid4

from unittest2 import TestCase
from sh import git, rm, touch  # pylint: disable=no-name-in-module


class BaseTestCase(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        """ Cleans up the temporary git repository """
        rm("-rf", cls.tmp_git_repo)

    def _create_simple_commit(self, message, out=None, ok_code=None, env=None):
        """ Creates a simple commit with an empty test file.
            :param message: Commit message for the commit. """
        test_filename = "test-file-" + str(uuid4())
        touch(test_filename, _cwd=self.tmp_git_repo)
        git("add", test_filename, _cwd=self.tmp_git_repo)
        # https://amoffat.github.io/sh/#interactive-callbacks
        git("commit", "-m", message, _cwd=self.tmp_git_repo, _tty_in=True, _out=out, _ok_code=ok_code, _env=env)
        return test_filename

    @staticmethod
    def get_sample_path(filename=""):
        samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
        return os.path.join(samples_dir, filename)
