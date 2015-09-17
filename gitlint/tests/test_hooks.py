from gitlint.tests.base import BaseTestCase
from gitlint.hooks import GitHookInstaller, GitHookInstallerError, COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH
from mock import patch, ANY


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
        with self.assertRaises(GitHookInstallerError):
            GitHookInstaller.install_commit_msg_hook()
            isdir.assert_called_once_with('.git/hooks')
            path_exists.assert_not_called()
            copy.assert_not_called()

        # mock that there is already a commit hook present
        isdir.return_value = True
        path_exists.return_value = True
        with self.assertRaises(GitHookInstallerError):
            GitHookInstaller.install_commit_msg_hook()
