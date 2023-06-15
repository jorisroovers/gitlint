import os
import shutil
import stat

from gitlint.config import LintConfig
from gitlint.exception import GitlintError
from gitlint.git import git_hooks_dir
from gitlint.utils import FILE_ENCODING

COMMIT_MSG_HOOK_SRC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "commit-msg")
COMMIT_MSG_HOOK_DST_PATH = "commit-msg"
GITLINT_HOOK_IDENTIFIER = "### gitlint commit-msg hook start ###\n"


class GitHookInstallerError(GitlintError):
    pass


class GitHookInstaller:
    """Utility class that provides methods for installing and uninstalling the gitlint commitmsg hook."""

    @staticmethod
    def commit_msg_hook_path(lint_config: LintConfig) -> str:
        return os.path.join(git_hooks_dir(lint_config.target), COMMIT_MSG_HOOK_DST_PATH)

    @staticmethod
    def _assert_git_repo(target):
        """Asserts that a given target directory is a git repository"""
        hooks_dir = git_hooks_dir(target)
        if not os.path.isdir(hooks_dir):
            raise GitHookInstallerError(f"{target} is not a git repository.")

    @staticmethod
    def install_commit_msg_hook(lint_config):
        GitHookInstaller._assert_git_repo(lint_config.target)
        dest_path = GitHookInstaller.commit_msg_hook_path(lint_config)
        if os.path.exists(dest_path):
            raise GitHookInstallerError(
                f"There is already a commit-msg hook file present in {dest_path}.\n"
                "gitlint currently does not support appending to an existing commit-msg file."
            )

        # copy hook file
        shutil.copy(COMMIT_MSG_HOOK_SRC_PATH, dest_path)
        # make hook executable
        st = os.stat(dest_path)
        os.chmod(dest_path, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def uninstall_commit_msg_hook(lint_config):
        GitHookInstaller._assert_git_repo(lint_config.target)
        dest_path = GitHookInstaller.commit_msg_hook_path(lint_config)
        if not os.path.exists(dest_path):
            raise GitHookInstallerError(f"There is no commit-msg hook present in {dest_path}.")

        with open(dest_path, encoding=FILE_ENCODING) as fp:
            lines = fp.readlines()
            if len(lines) < 2 or lines[1] != GITLINT_HOOK_IDENTIFIER:  # noqa: PLR2004 (Magic value used in comparison)
                msg = (
                    f"The commit-msg hook in {dest_path} was not installed by gitlint (or it was modified).\n"
                    "Uninstallation of 3th party or modified gitlint hooks is not supported."
                )
                raise GitHookInstallerError(msg)

        # If we are sure it's a gitlint hook, go ahead and remove it
        os.remove(dest_path)
