from gitlint.tests.base import BaseTestCase
from gitlint.hooks import GitHookInstaller, GitHookInstallerError, COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH, \
    GITLINT_HOOK_IDENTIFIER
from mock import patch, ANY, mock_open


class HookTests(BaseTestCase):
    @patch('os.chmod')
    @patch('os.stat')
    @patch('gitlint.hooks.shutil.copy')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    def test_install_commit_msg_hook(self, isdir, path_exists, copy, stat, chmod):
        GitHookInstaller.install_commit_msg_hook()
        isdir.assert_called_once_with('.git/hooks')
        path_exists.assert_called_once_with(COMMIT_MSG_HOOK_DST_PATH)
        copy.assert_called_once_with(COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH)
        stat.assert_called_once_with(COMMIT_MSG_HOOK_DST_PATH)
        chmod.assert_called_once_with(COMMIT_MSG_HOOK_DST_PATH, ANY)

    @patch('gitlint.hooks.shutil.copy')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    def test_install_commit_msg_hook_negative(self, isdir, path_exists, copy):
        # mock that current dir is not a git repo
        isdir.return_value = False
        expected_msg = "The current directory is not a git repository"
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook()
            isdir.assert_called_once_with('.git/hooks')
            path_exists.assert_not_called()
            copy.assert_not_called()

        # mock that there is already a commit hook present
        isdir.return_value = True
        path_exists.return_value = True
        expected_msg = "There is already a commit-msg hook file present in {}".format(COMMIT_MSG_HOOK_DST_PATH) + \
                       ". gitlint currently does not support appending to an existing commit-msg file."
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook()

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_uninstall_commit_msg_hook(self, isdir, path_exists, remove):
        read_data = "#!/bin/sh\n" + GITLINT_HOOK_IDENTIFIER
        with patch('gitlint.hooks.open', mock_open(read_data=read_data), create=True):
            GitHookInstaller.uninstall_commit_msg_hook()

        isdir.assert_called_once_with('.git/hooks')
        path_exists.assert_called_once_with(COMMIT_MSG_HOOK_DST_PATH)
        remove.assert_called_once_with(COMMIT_MSG_HOOK_DST_PATH)

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_uninstall_commit_msg_hook_negative(self, isdir, path_exists, remove):
        # mock that the current directory is not a git repo
        isdir.return_value = False
        expected_msg = "The current directory is not a git repository"
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.install_commit_msg_hook()
            isdir.assert_called_once_with('.git/hooks')
            path_exists.assert_not_called()
            remove.assert_not_called()

        # mock that there is no commit hook present
        isdir.return_value = True
        path_exists.return_value = False
        expected_msg = "There is no commit-msg hook present in {}".format(COMMIT_MSG_HOOK_DST_PATH)
        with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
            GitHookInstaller.uninstall_commit_msg_hook()
            isdir.assert_called_once_with('.git/hooks')
            path_exists.assert_called_once_with(COMMIT_MSG_HOOK_DST_PATH)
            remove.assert_not_called()

        # mock that there is a different (=not gitlint) commit hook
        isdir.return_value = True
        path_exists.return_value = True
        read_data = "#!/bin/sh\nfoo"
        expected_msg = "The commit-msg hook in {} was not installed by gitlint ".format(COMMIT_MSG_HOOK_DST_PATH) + \
                       "\(or it was modified\).\nUninstallation of 3th party or modified gitlint hooks " + \
                       "is not supported."
        with patch('gitlint.hooks.open', mock_open(read_data=read_data), create=True):
            with self.assertRaisesRegexp(GitHookInstallerError, expected_msg):
                GitHookInstaller.uninstall_commit_msg_hook()
            remove.assert_not_called()
