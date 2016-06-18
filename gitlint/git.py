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

    @staticmethod
    def from_full_message(commit_msg_str):
        """  Parses a full git commit message by parsing a given string into the different parts of a commit message """
        lines = [line for line in commit_msg_str.splitlines() if not line.startswith("#")]
        full = "\n".join(lines)
        title = lines[0] if len(lines) > 0 else ""
        body = lines[1:] if len(lines) > 1 else []
        return GitCommitMessage(original=commit_msg_str, full=full, title=title, body=body)

    def __str__(self):
        return self.full  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class GitCommit(object):
    """ Class representing a git commit.
        A commit consists of: message, author name, author email, date, list of changed files
        In the context of gitlint, only the commit message is required.
    """

    def __init__(self, message, date=None, author_name=None, author_email=None, parents=None, is_merge_commit=False,
                 changed_files=None):
        self.message = message
        self.author_name = author_name
        self.author_email = author_email
        self.date = date

        # parent commit hashes
        if not parents:
            self.parents = []
        else:
            self.parents = parents

        self.is_merge_commit = is_merge_commit

        if not changed_files:
            self.changed_files = []
        else:
            self.changed_files = changed_files

    def __str__(self):
        format_str = "Author: %s <%s>\nDate:   %s\n%s"  # pragma: no cover
        return format_str % (self.author_name, self.author_email, self.date, str(self.message))  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover


class GitContext(object):
    """ Class representing the git context in which gitlint is operating: a data object storing information about
    the git repository that gitlint is linting.
    """

    def __init__(self):
        self.commits = []

    @staticmethod
    def from_commit_msg(commit_msg_str):
        """ Determines git context based on a commit message.
        :param commit_msg_str: Full git commit message.
        """
        commit_msg_obj = GitCommitMessage.from_full_message(commit_msg_str)

        # For now, we consider a commit a merge commit if its title starts with "Merge"
        is_merge_commit = commit_msg_obj.title.startswith("Merge")
        commit = GitCommit(commit_msg_obj, is_merge_commit=is_merge_commit)

        context = GitContext()
        context.commits.append(commit)
        return context

    @staticmethod
    def from_local_repository(repository_path):
        """ Retrieves the git context from a local git repository.
        :param repository_path: Path to the git repository to retrieve the context from
        """
        try:
            # Special arguments passed to sh: http://amoffat.github.io/sh/special_arguments.html
            sh_special_args = {
                '_tty_out': False,
                '_cwd': repository_path
            }

            # Get info from the local git repository
            # https://git-scm.com/docs/pretty-formats
            commit_msg = sh.git.log("-1", "--pretty=%B", **sh_special_args)
            commit_author_name = sh.git.log("-1", "--pretty=%aN", **sh_special_args)
            commit_author_email = sh.git.log("-1", "--pretty=%aE", **sh_special_args)
            commit_date = sh.git.log("-1", "--pretty=%aD", **sh_special_args)
            commit_parents = sh.git.log("-1", "--pretty=%P", **sh_special_args).split(" ")
            commit_is_merge_commit = len(commit_parents) > 1

            # changed files in last commit
            changed_files_str = sh.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD", **sh_special_args)
        except CommandNotFound:
            error_msg = "'git' command not found. You need to install git to use gitlint on a local repository. " + \
                        "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
            raise GitContextError(error_msg)
        except ErrorReturnCode as e:  # Something went wrong while executing the git command
            error_msg = e.stderr.strip()
            if b"Not a git repository" in error_msg:
                error_msg = "{0} is not a git repository.".format(repository_path)
            else:
                error_msg = "An error occurred while executing '{0}': {1}".format(e.full_cmd, error_msg)
            raise GitContextError(error_msg)

        # Create Git commit object with the retrieved info
        changed_files = [changed_file for changed_file in changed_files_str.strip().split("\n")]
        commit_msg_obj = GitCommitMessage.from_full_message(commit_msg)
        commit = GitCommit(commit_msg_obj, author_name=commit_author_name, author_email=commit_author_email,
                           date=commit_date, changed_files=changed_files, parents=commit_parents,
                           is_merge_commit=commit_is_merge_commit)

        # Create GitContext info with the commit object and return
        context = GitContext()
        context.commits.append(commit)
        return context
