import shutil
import stat
import os

COMMIT_MSG_HOOK_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks/commit-msg")
COMMIT_MSG_HOOK_DST_PATH = os.path.abspath(".git/hooks/commit-msg")
GITLINT_HOOK_IDENTIFIER = "### gitlint commit-msg hook start ###\n"


class GitHookInstallerError(Exception):
    pass


class GitHookInstaller(object):
    @staticmethod
    def install_commit_msg_hook():
        # assert that current directory is a git repository
        if not os.path.isdir(".git/hooks"):
            raise GitHookInstallerError("The current directory is not a git repository")
        if os.path.exists(COMMIT_MSG_HOOK_DST_PATH):
            raise GitHookInstallerError(
                "There is already a commit-msg hook file present in {}. ".format(COMMIT_MSG_HOOK_DST_PATH) +
                "gitlint currently does not support appending to an existing commit-msg file.")

        # copy hook file
        shutil.copy(COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH)
        # make hook executable
        st = os.stat(COMMIT_MSG_HOOK_DST_PATH)
        os.chmod(COMMIT_MSG_HOOK_DST_PATH, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def uninstall_commit_msg_hook():
        # assert that current directory is a git repository
        if not os.path.isdir(".git/hooks"):
            raise GitHookInstallerError("The current directory is not a git repository")
        if not os.path.exists(COMMIT_MSG_HOOK_DST_PATH):
            raise GitHookInstallerError("There is no commit-msg hook present in {}".format(COMMIT_MSG_HOOK_DST_PATH))

        with open(COMMIT_MSG_HOOK_DST_PATH) as file:
            lines = file.readlines()
            if len(lines) < 2 or lines[1] != GITLINT_HOOK_IDENTIFIER:
                msg = "The commit-msg hook in {} was not installed by gitlint (or it was modified).\n" + \
                      "Uninstallation of 3th party or modified gitlint hooks is not supported."
                raise GitHookInstallerError(msg.format(COMMIT_MSG_HOOK_DST_PATH))

        # If we are sure it's a gitlint hook, go ahead and remove it
        os.remove(COMMIT_MSG_HOOK_DST_PATH)
