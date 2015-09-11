import shutil
import stat
import sys
import os

COMMIT_MSG_HOOK_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks/commit-msg")
COMMIT_MSG_HOOK_DST_PATH = os.path.abspath(".git/hooks/commit-msg")


class GitHookInstaller(object):
    @staticmethod
    def install_commit_msg_hook():
        # assert that current directory is a git repository
        if not os.path.isdir(".git/hooks"):
            sys.stderr.write("The current directory is not a git repository\n")
            exit(1)
        if os.path.exists(COMMIT_MSG_HOOK_DST_PATH):
            sys.stderr.write(
                "There is already a commit-msg hook file present in {}. \n".format(COMMIT_MSG_HOOK_DST_PATH) +
                "gitlint currently does not support appending to an existing commit-msg file.\n")
            exit(1)

        # copy hook file
        shutil.copy(COMMIT_MSG_HOOK_SRC_PATH, COMMIT_MSG_HOOK_DST_PATH)
        # make hook executable
        st = os.stat(COMMIT_MSG_HOOK_DST_PATH)
        os.chmod(COMMIT_MSG_HOOK_DST_PATH, st.st_mode | stat.S_IEXEC)

        # declare victory :-)
        sys.stdout.write("Successfully installed gitlint commit-msg hook in {0}\n".format(COMMIT_MSG_HOOK_DST_PATH))
        exit(0)
