# -*- coding: utf-8 -*-
import os

from unittest.mock import patch

from gitlint.shell import ErrorReturnCode, CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext, GitContextError, GitNotInstalledError, git_commentchar, git_hooks_dir


class GitTests(BaseTestCase):

    # Expected special_args passed to 'sh'
    expected_sh_special_args = {
        '_tty_out': False,
        '_cwd': "fåke/path"
    }

    @patch('gitlint.git.sh')
    def test_get_latest_commit_command_not_found(self, sh):
        sh.git.side_effect = CommandNotFound("git")
        expected_msg = "'git' command not found. You need to install git to use gitlint on a local repository. " + \
                       "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
        with self.assertRaisesMessage(GitNotInstalledError, expected_msg):
            GitContext.from_local_repository("fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)

    @patch('gitlint.git.sh')
    def test_get_latest_commit_git_error(self, sh):
        # Current directory not a git repo
        err = b"fatal: Not a git repository (or any of the parent directories): .git"
        sh.git.side_effect = ErrorReturnCode("git log -1 --pretty=%H", b"", err)

        with self.assertRaisesMessage(GitContextError, "fåke/path is not a git repository."):
            GitContext.from_local_repository("fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)
        sh.git.reset_mock()

        err = b"fatal: Random git error"
        sh.git.side_effect = ErrorReturnCode("git log -1 --pretty=%H", b"", err)

        expected_msg = "An error occurred while executing 'git log -1 --pretty=%H': {0}".format(err)
        with self.assertRaisesMessage(GitContextError, expected_msg):
            GitContext.from_local_repository("fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)

    @patch('gitlint.git.sh')
    def test_git_no_commits_error(self, sh):
        # No commits: returned by 'git log'
        err = b"fatal: your current branch 'master' does not have any commits yet"

        sh.git.side_effect = ErrorReturnCode("git log -1 --pretty=%H", b"", err)

        expected_msg = "Current branch has no commits. Gitlint requires at least one commit to function."
        with self.assertRaisesMessage(GitContextError, expected_msg):
            GitContext.from_local_repository("fåke/path")

        # assert that commit message was read using git command
        sh.git.assert_called_once_with("log", "-1", "--pretty=%H", **self.expected_sh_special_args)
        sh.git.reset_mock()

        # Unknown reference 'HEAD' commits: returned by 'git rev-parse'
        err = (b"HEAD"
               b"fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree."
               b"Use '--' to separate paths from revisions, like this:"
               b"'git <command> [<revision>...] -- [<file>...]'")

        sh.git.side_effect = [
            "#\n",  # git config --get core.commentchar
            ErrorReturnCode("rev-parse --abbrev-ref HEAD", b"", err)
        ]

        with self.assertRaisesMessage(GitContextError, expected_msg):
            context = GitContext.from_commit_msg("test")
            context.current_branch

        # assert that commit message was read using git command
        sh.git.assert_called_with("rev-parse", "--abbrev-ref", "HEAD", _tty_out=False, _cwd=None)

    @patch("gitlint.git._git")
    def test_git_commentchar(self, git):
        git.return_value.exit_code = 1
        self.assertEqual(git_commentchar(), "#")

        git.return_value.exit_code = 0
        git.return_value = "ä"
        self.assertEqual(git_commentchar(), "ä")

        git.return_value = ';\n'
        self.assertEqual(git_commentchar(os.path.join("/föo", "bar")), ';')

        git.assert_called_with("config", "--get", "core.commentchar", _ok_code=[0, 1],
                               _cwd=os.path.join("/föo", "bar"))

    @patch("gitlint.git._git")
    def test_git_hooks_dir(self, git):
        hooks_dir = os.path.join("föo", ".git", "hooks")
        git.return_value = hooks_dir + "\n"
        self.assertEqual(git_hooks_dir("/blä"), os.path.abspath(os.path.join("/blä", hooks_dir)))

        git.assert_called_once_with("rev-parse", "--git-path", "hooks", _cwd="/blä")
