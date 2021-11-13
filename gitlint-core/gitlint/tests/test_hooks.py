# -*- coding: utf-8 -*-

import os

from unittest.mock import patch, ANY, mock_open

from gitlint.tests.base import BaseTestCase
from gitlint.config import LintConfig
from gitlint.hooks import GitHookInstaller, GitHookInstallerError, COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH, \
    GITLINT_HOOK_IDENTIFIER


class HookTests(BaseTestCase):

    @patch('gitlint.hooks.git_hooks_dir')
    def test_commit_msg_hook_path(self, git_hooks_dir):
        git_hooks_dir.return_value = os.path.join("/föo", "bar")
        lint_config = LintConfig()
        lint_config.target = self.SAMPLES_DIR
        expected_path = os.path.join(git_hooks_dir.return_value, COMMIT_MSG_HOOK_DST_PATH)
        path = GitHookInstaller.commit_msg_hook_path(lint_config)

        git_hooks_dir.assert_called_once_with(self.SAMPLES_DIR)
        self.assertEqual(path, expected_path)

    @staticmethod
    @patch('os.chmod')
    @patch('os.stat')
    @patch('gitlint.hooks.shutil.copy')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    @patch('gitlint.hooks.git_hooks_dir')
    def test_install_commit_msg_hook(git_hooks_dir, isdir, path_exists, copy, stat, chmod):
        lint_config = LintConfig()
        lint_config.target = os.path.join("/hür", "dur")
        git_hooks_dir.return_value = os.path.join("/föo", "bar", ".git", "hooks")
        expected_dst = os.path.join(git_hooks_dir.return_value, COMMIT_MSG_HOOK_DST_PATH)
        GitHookInstaller.install_commit_msg_hook(lint_config)
        isdir.assert_called_with(git_hooks_dir.return_value)
        path_exists.assert_called_once_with(expected_dst)
        copy.assert_called_once_with(COMMIT_MSG_HOOK_SRC_PATH, expected_dst)
        stat.assert_called_once_with(expected_dst)
        chmod.assert_called_once_with(expected_dst, ANY)
        git_hooks_dir.assert_called_with(lint_config.target)

    @patch('gitlint.hooks.shutil.copy')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    @patch('gitlint.hooks.git_hooks_dir')
    def test_install_commit_msg_hook_negative(self, git_hooks_dir, isdir, path_exists, copy):
        lint_config = LintConfig()
        lint_config.target = os.path.join("/hür", "dur")
        git_hooks_dir.return_value = os.path.join("/föo", "bar", ".git", "hooks")
        # mock that current dir is not a git repo
        isdir.return_value = False
        expected_msg = f"{lint_config.target} is not a git repository."
        with self.assertRaisesMessage(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook(lint_config)
            isdir.assert_called_with(git_hooks_dir.return_value)
            path_exists.assert_not_called()
            copy.assert_not_called()

        # mock that there is already a commit hook present
        isdir.return_value = True
        path_exists.return_value = True
        expected_dst = os.path.join(git_hooks_dir.return_value, COMMIT_MSG_HOOK_DST_PATH)
        expected_msg = f"There is already a commit-msg hook file present in {expected_dst}.\n" + \
                       "gitlint currently does not support appending to an existing commit-msg file."
        with self.assertRaisesMessage(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook(lint_config)

    @staticmethod
    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    @patch('gitlint.hooks.git_hooks_dir')
    def test_uninstall_commit_msg_hook(git_hooks_dir, isdir, path_exists, remove):
        lint_config = LintConfig()
        git_hooks_dir.return_value = os.path.join("/föo", "bar", ".git", "hooks")
        lint_config.target = os.path.join("/hür", "dur")
        read_data = "#!/bin/sh\n" + GITLINT_HOOK_IDENTIFIER
        with patch('gitlint.hooks.io.open', mock_open(read_data=read_data), create=True):
            GitHookInstaller.uninstall_commit_msg_hook(lint_config)

        expected_dst = os.path.join(git_hooks_dir.return_value, COMMIT_MSG_HOOK_DST_PATH)
        isdir.assert_called_with(git_hooks_dir.return_value)
        path_exists.assert_called_once_with(expected_dst)
        remove.assert_called_with(expected_dst)
        git_hooks_dir.assert_called_with(lint_config.target)

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    @patch('gitlint.hooks.git_hooks_dir')
    def test_uninstall_commit_msg_hook_negative(self, git_hooks_dir, isdir, path_exists, remove):
        lint_config = LintConfig()
        lint_config.target = os.path.join("/hür", "dur")
        git_hooks_dir.return_value = os.path.join("/föo", "bar", ".git", "hooks")

        # mock that the current directory is not a git repo
        isdir.return_value = False
        expected_msg = f"{lint_config.target} is not a git repository."
        with self.assertRaisesMessage(GitHookInstallerError, expected_msg):
            GitHookInstaller.uninstall_commit_msg_hook(lint_config)
            isdir.assert_called_with(git_hooks_dir.return_value)
            path_exists.assert_not_called()
            remove.assert_not_called()

        # mock that there is no commit hook present
        isdir.return_value = True
        path_exists.return_value = False
        expected_dst = os.path.join(git_hooks_dir.return_value, COMMIT_MSG_HOOK_DST_PATH)
        expected_msg = f"There is no commit-msg hook present in {expected_dst}."
        with self.assertRaisesMessage(GitHookInstallerError, expected_msg):
            GitHookInstaller.uninstall_commit_msg_hook(lint_config)
            isdir.assert_called_with(git_hooks_dir.return_value)
            path_exists.assert_called_once_with(expected_dst)
            remove.assert_not_called()

        # mock that there is a different (=not gitlint) commit hook
        isdir.return_value = True
        path_exists.return_value = True
        read_data = "#!/bin/sh\nfoo"
        expected_dst = os.path.join(git_hooks_dir.return_value, COMMIT_MSG_HOOK_DST_PATH)
        expected_msg = f"The commit-msg hook in {expected_dst} was not installed by gitlint " + \
                       "(or it was modified).\nUninstallation of 3th party or modified gitlint hooks " + \
                       "is not supported."
        with patch('gitlint.hooks.io.open', mock_open(read_data=read_data), create=True):
            with self.assertRaisesMessage(GitHookInstallerError, expected_msg):
                GitHookInstaller.uninstall_commit_msg_hook(lint_config)
            remove.assert_not_called()
