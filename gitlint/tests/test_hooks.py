from gitlint.tests.base import BaseTestCase
from gitlint.config import LintConfig
from gitlint.hooks import GitHookInstaller, GitHookInstallerError, COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH, \
    GITLINT_HOOK_IDENTIFIER
from mock import patch, ANY, mock_open
import os


class HookTests(BaseTestCase):
    def test_commit_msg_hook_path(self):
        lint_config = LintConfig(target="/foo/bar")
        expected_path = os.path.join("/foo/bar", COMMIT_MSG_HOOK_DST_PATH)
        path = GitHookInstaller.commit_msg_hook_path(lint_config)
        self.assertEqual(path, expected_path)

    @patch('os.chmod')
    @patch('os.stat')
    @patch('gitlint.hooks.shutil.copy')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    def test_install_commit_msg_hook(self, isdir, path_exists, copy, stat, chmod):
        lint_config = LintConfig(target="/foo/bar")
        expected_dst = os.path.join("/foo/bar", COMMIT_MSG_HOOK_DST_PATH)
        GitHookInstaller.install_commit_msg_hook(lint_config)
        isdir.assert_called_once_with('/foo/bar/.git/hooks')
        path_exists.assert_called_once_with(expected_dst)
        copy.assert_called_once_with(COMMIT_MSG_HOOK_SRC_PATH, expected_dst)
        stat.assert_called_once_with(expected_dst)
        chmod.assert_called_once_with(expected_dst, ANY)

    @patch('gitlint.hooks.shutil.copy')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    def test_install_commit_msg_hook_negative(self, isdir, path_exists, copy):
        lint_config = LintConfig(target="/foo/bar")
        # mock that current dir is not a git repo
        isdir.return_value = False
        expected_msg = "/foo/bar is not a git repository"
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook(lint_config)
            isdir.assert_called_once_with('/foo/bar/.git/hooks')
            path_exists.assert_not_called()
            copy.assert_not_called()

        # mock that there is already a commit hook present
        isdir.return_value = True
        path_exists.return_value = True
        expected_dst = os.path.join("/foo/bar", COMMIT_MSG_HOOK_DST_PATH)
        expected_msg = "There is already a commit-msg hook file present in {}.\n".format(expected_dst) + \
                       "gitlint currently does not support appending to an existing commit-msg file."
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook(lint_config)

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_uninstall_commit_msg_hook(self, isdir, path_exists, remove):
        lint_config = LintConfig(target="/foo/bar")
        read_data = "#!/bin/sh\n" + GITLINT_HOOK_IDENTIFIER
        with patch('gitlint.hooks.open', mock_open(read_data=read_data), create=True):
            GitHookInstaller.uninstall_commit_msg_hook(lint_config)

        expected_dst = os.path.join("/foo/bar", COMMIT_MSG_HOOK_DST_PATH)
        isdir.assert_called_once_with('/foo/bar/.git/hooks')
        path_exists.assert_called_once_with(expected_dst)
        remove.assert_called_once_with(expected_dst)

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_uninstall_commit_msg_hook_negative(self, isdir, path_exists, remove):
        lint_config = LintConfig(target="/foo/bar")
        # mock that the current directory is not a git repo
        isdir.return_value = False
        expected_msg = "/foo/bar is not a git repository"
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.uninstall_commit_msg_hook(lint_config)
            isdir.assert_called_once_with('/foo/bar/.git/hooks')
            path_exists.assert_not_called()
            remove.assert_not_called()

        # mock that there is no commit hook present
        isdir.return_value = True
        path_exists.return_value = False
        expected_dst = os.path.join("/foo/bar", COMMIT_MSG_HOOK_DST_PATH)
        expected_msg = "There is no commit-msg hook present in {}.".format(expected_dst)
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.uninstall_commit_msg_hook(lint_config)
            isdir.assert_called_once_with('/foo/bar/.git/hooks')
            path_exists.assert_called_once_with(expected_dst)
            remove.assert_not_called()

        # mock that there is a different (=not gitlint) commit hook
        isdir.return_value = True
        path_exists.return_value = True
        read_data = "#!/bin/sh\nfoo"
        expected_dst = os.path.join("/foo/bar", COMMIT_MSG_HOOK_DST_PATH)
        expected_msg = "The commit-msg hook in {} was not installed by gitlint ".format(expected_dst) + \
                       "\(or it was modified\).\nUninstallation of 3th party or modified gitlint hooks " + \
                       "is not supported."
        with patch('gitlint.hooks.open', mock_open(read_data=read_data), create=True):
            with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
                GitHookInstaller.uninstall_commit_msg_hook(lint_config)
            remove.assert_not_called()
