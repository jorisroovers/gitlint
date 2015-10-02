import sh


class GitCommitMessage(object):
    """ Class representing a git commit message. A commit message consists of the following:
      - original: The actual commit message as returned by `git log`
      - full: original, but stripped of any comments
      - title: the first line of full
      - body: all lines following the title
    """

    def __init__(self, original=None, full=None, title=None, body=None):
        self.original = original
        self.full = full
        self.title = title
        self.body = body

    def __str__(self):
        return self.full  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class GitContext(object):
    """ Class representing the git context in which gitlint is operating: a data object storing information about
    the git repository that gitlint is linting.
    """

    def __init__(self):
        self.commit_msg = None
        self.changed_files = []

    def set_commit_msg(self, commit_msg_str):
        """  Sets the commit message by parsing a given string into the different parts of a commit message """
        lines = [line for line in commit_msg_str.split("\n") if not line.startswith("#")]
        full = "\n".join(lines)
        title = lines[0] if len(lines) > 0 else ""
        body = lines[1:] if len(lines) > 1 else []
        self.commit_msg = GitCommitMessage(original=commit_msg_str, full=full, title=title, body=body)

    @staticmethod
    def from_local_repository():
        commit_info = GitContext()
        commit_info.set_commit_msg(sh.git.log("-1", "--pretty=%B", _tty_out=False))

        # changed files in last commit
        changed_files_str = sh.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD", _tty_out=False)
        commit_info.changed_files = [changed_file for changed_file in changed_files_str.strip().split("\n")]
        return commit_info
