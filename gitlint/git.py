import sh
# import exceptions separately, this makes it a little easier to mock them out in the unit tests
from sh import CommandNotFound, ErrorReturnCode


class GitContextError(Exception):
    """ Exception indicating there is an issue with the git context """
    pass


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
    def from_local_repository(repository_path):
        try:
            # Special arguments passed to sh: http://amoffat.github.io/sh/special_arguments.html
            sh_special_args = {
                '_tty_out': False,
                '_cwd': repository_path
            }
            # Get info from the local git repository
            # last commit message
            commit_msg = sh.git.log("-1", "--pretty=%B", **sh_special_args)
            # changed files in last commit
            changed_files_str = sh.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD", **sh_special_args)
        except CommandNotFound:
            error_msg = "'git' command not found. You need to install git to use gitlint on a local repository. " + \
                        "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
            raise GitContextError(error_msg)
        except ErrorReturnCode as e:  # Something went wrong while executing the git command
            error_msg = e.stderr.strip()
            if b"Not a git repository" in error_msg:
                error_msg = "{} is not a git repository.".format(repository_path)
            else:
                error_msg = "An error occurred while executing '{}': {}".format(e.full_cmd, error_msg)
            raise GitContextError(error_msg)

        # Create GitContext object with the retrieved info and return
        commit_info = GitContext()
        commit_info.set_commit_msg(commit_msg)
        commit_info.changed_files = [changed_file for changed_file in changed_files_str.strip().split("\n")]
        return commit_info
