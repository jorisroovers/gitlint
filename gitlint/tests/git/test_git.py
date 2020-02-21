# -*- coding: utf-8 -*-
import os

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.shell import ErrorReturnCode, CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext, GitContextError, GitNotInstalledError, git_commentchar, git_hooks_dir


class GitTests(BaseTestCase):

    # Expected special_args passed to 'sh'
    expected_sh_special_args = {
        '_tty_out': False,
        '_cwd': u"fåke/path"
    }

    @patch('gitlint.git.sh')
    def test_get_latest_commit_command_not_found(self, sh):
        sh.git.side_effect = CommandNotFound("git")
        expected_msg = "'git' command not found. You need to install git to use gitlint on a local repository. " + \
                       "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
        with self.assertRaisesRegex(GitNotInstalledError, expected_msg):
            GitContext.from_local_repository(u"fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)

    @patch('gitlint.git.sh')
    def test_get_latest_commit_git_error(self, sh):
        # Current directory not a git repo
        err = b"fatal: Not a git repository (or any of the parent directories): .git"
        sh.git.side_effect = ErrorReturnCode("git log -1 --pretty=%H", b"", err)

        with self.assertRaisesRegex(GitContextError, u"fåke/path is not a git repository."):
            GitContext.from_local_repository(u"fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)
        sh.git.reset_mock()

        err = b"fatal: Random git error"
        sh.git.side_effect = ErrorReturnCode("git log -1 --pretty=%H", b"", err)

        expected_msg = u"An error occurred while executing 'git log -1 --pretty=%H': {0}".format(err)
        with self.assertRaisesRegex(GitContextError, expected_msg):
            GitContext.from_local_repository(u"fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)

    @patch("gitlint.git._git")
    def test_git_commentchar(self, git):
        git.return_value.exit_code = 1
        self.assertEqual(git_commentchar(), "#")

        git.return_value.exit_code = 0
        git.return_value.__str__ = lambda _: u"ä"
        git.return_value.__unicode__ = lambda _: u"ä"
        self.assertEqual(git_commentchar(), u"ä")

        git.return_value = ';\n'
        self.assertEqual(git_commentchar(os.path.join(u"/föo", u"bar")), ';')

        git.assert_called_with("config", "--get", "core.commentchar", _ok_code=[0, 1],
                               _cwd=os.path.join(u"/föo", u"bar"))

    @patch("gitlint.git._git")
    def test_git_hooks_dir(self, git):
        hooks_dir = os.path.join(u"föo", ".git", "hooks")
        git.return_value.__str__ = lambda _: hooks_dir + "\n"
        git.return_value.__unicode__ = lambda _: hooks_dir + "\n"
        self.assertEqual(git_hooks_dir(u"/blä"), os.path.abspath(os.path.join(u"/blä", hooks_dir)))

        git.assert_called_once_with("rev-parse", "--git-path", "hooks", _cwd=u"/blä")
