import sh


class GitCommitInfo(object):
    def __init__(self):
        self.commit_msg = None
        self.files_changed = None

    @staticmethod
    def get_latest_commit():
        commit_info = GitCommitInfo()
        commit_info.commit_msg = sh.git.log("-1", "--pretty=%B", _tty_out=False)
        # changed files in last commit
        changed_files_str = sh.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD", _tty_out=False)
        commit_info.changed_files = [changed_file for changed_file in changed_files_str.strip().split("\n")]
        return commit_info
