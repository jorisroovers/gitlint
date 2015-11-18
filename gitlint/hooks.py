import shutil
import stat
import os

COMMIT_MSG_HOOK_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/commit-msg")
COMMIT_MSG_HOOK_DST_PATH = ".git/hooks/commit-msg"
HOOKS_DIR_PATH = ".git/hooks"
GITLINT_HOOK_IDENTIFIER = "### gitlint commit-msg hook start ###\n"


class GitHookInstallerError(Exception):
    pass


class GitHookInstaller(object):
    @staticmethod
    def commit_msg_hook_path(lint_config):
        return os.path.abspath(os.path.join(lint_config.target, COMMIT_MSG_HOOK_DST_PATH))

    @staticmethod
    def _assert_git_repo(lint_config):
        # assert that current directory is a git repository
        hooks_dir = os.path.abspath(os.path.join(lint_config.target, HOOKS_DIR_PATH))
        if not os.path.isdir(hooks_dir):
            raise GitHookInstallerError("{} is not a git repository.".format(lint_config.target))

    @staticmethod
    def install_commit_msg_hook(lint_config):
        GitHookInstaller._assert_git_repo(lint_config)
        dest_path = GitHookInstaller.commit_msg_hook_path(lint_config)
        if os.path.exists(dest_path):
            raise GitHookInstallerError(
                "There is already a commit-msg hook file present in {}.\n".format(dest_path) +
                "gitlint currently does not support appending to an existing commit-msg file.")

        # copy hook file
        shutil.copy(COMMIT_MSG_HOOK_SRC_PATH, dest_path)
        # make hook executable
        st = os.stat(dest_path)
        os.chmod(dest_path, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def uninstall_commit_msg_hook(lint_config):
        GitHookInstaller._assert_git_repo(lint_config)
        dest_path = GitHookInstaller.commit_msg_hook_path(lint_config)
        if not os.path.exists(dest_path):
            raise GitHookInstallerError("There is no commit-msg hook present in {}.".format(dest_path))

        with open(dest_path) as file:
            lines = file.readlines()
            if len(lines) < 2 or lines[1] != GITLINT_HOOK_IDENTIFIER:
                msg = "The commit-msg hook in {} was not installed by gitlint (or it was modified).\n" + \
                      "Uninstallation of 3th party or modified gitlint hooks is not supported."
                raise GitHookInstallerError(msg.format(dest_path))

        # If we are sure it's a gitlint hook, go ahead and remove it
        os.remove(dest_path)
