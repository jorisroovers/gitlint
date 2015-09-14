import sh


class GitCommitInfo(object):
    def __init__(self):
        self.commit_msg = None
        self.files_changed = None

    @staticmethod
    def get_latest_commit():
        commit_info = GitCommitInfo()
        commit_info.commit_msg = sh.git.log("-1", "--pretty=%B", _tty_out=False)
        return commit_info
