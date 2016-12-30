import arrow
import sh
# import exceptions separately, this makes it a little easier to mock them out in the unit tests
from sh import CommandNotFound, ErrorReturnCode

from gitlint.utils import ustr, sstr


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

    def __unicode__(self):
        return self.full  # pragma: no cover

    def __str__(self):
        return sstr(self)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover

    def __eq__(self, other):
        return isinstance(other, GitCommitMessage) and self.original == other.original and \
               self.full == other.full and self.title == other.title and self.body == other.body  # noqa


class GitCommit(object):
    """ Class representing a git commit.
        A commit consists of: context, message, author name, author email, date, list of changed files
        In the context of gitlint, only the git context and commit message are required.
    """

    def __init__(self, context, message, date=None, author_name=None, author_email=None, parents=None,
                 is_merge_commit=False, changed_files=None):
        self.context = context
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

    def __unicode__(self):
        format_str = u"Author: %s <%s>\nDate:   %s\n%s"  # pragma: no cover
        return format_str % (self.author_name, self.author_email, self.date, ustr(self.message))  # pragma: no cover

    def __str__(self):
        return sstr(self)  # pragma: no cover

    def __repr__(self):
        return self.__str__()  # pragma: no cover

    def __eq__(self, other):
        # skip checking the context as context refers back to this obj, this will trigger a cyclic dependency
        return isinstance(other, GitCommit) and self.message == other.message and \
               self.author_name == other.author_name and self.author_email == other.author_email and \
               self.date == other.date and self.parents == other.parents and \
               self.is_merge_commit == other.is_merge_commit and self.changed_files == other.changed_files  # noqa


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
        context = GitContext()
        commit_msg_obj = GitCommitMessage.from_full_message(commit_msg_str)

        # For now, we consider a commit a merge commit if its title starts with "Merge"
        is_merge_commit = commit_msg_obj.title.startswith("Merge")
        commit = GitCommit(context, commit_msg_obj, is_merge_commit=is_merge_commit)

        context.commits.append(commit)
        return context

    @staticmethod
    def from_local_repository(repository_path):
        """ Retrieves the git context from a local git repository.
        :param repository_path: Path to the git repository to retrieve the context from
        """
        context = GitContext()
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
            # %aI -> ISO 8601-like format, while %aI is strict ISO 8601, it seems to be less widely supporte
            commit_date_str = sh.git.log("-1", "--pretty=%ai", **sh_special_args)
            commit_parents = sh.git.log("-1", "--pretty=%P", **sh_special_args).split(" ")
            commit_is_merge_commit = len(commit_parents) > 1

            # changed files in last commit
            changed_files_str = sh.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD", **sh_special_args)
        except CommandNotFound:
            error_msg = u"'git' command not found. You need to install git to use gitlint on a local repository. " + \
                        u"See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
            raise GitContextError(error_msg)
        except ErrorReturnCode as e:  # Something went wrong while executing the git command
            error_msg = e.stderr.strip()
            if b"Not a git repository" in error_msg:
                error_msg = u"{0} is not a git repository.".format(repository_path)
            else:
                error_msg = u"An error occurred while executing '{0}': {1}".format(e.full_cmd, error_msg)
            raise GitContextError(error_msg)

        # "YYYY-MM-DD HH:mm:ss Z" -> ISO 8601-like format
        # Use arrow for datetime parsing, because apparently python is quirky around ISO-8601 dates:
        # http://stackoverflow.com/a/30696682/381010
        commit_date = arrow.get(ustr(commit_date_str), "YYYY-MM-DD HH:mm:ss Z").datetime

        # Create Git commit object with the retrieved info
        changed_files = [changed_file for changed_file in changed_files_str.strip().split("\n")]
        commit_msg_obj = GitCommitMessage.from_full_message(commit_msg)
        commit = GitCommit(context, commit_msg_obj, author_name=commit_author_name, author_email=commit_author_email,
                           date=commit_date, changed_files=changed_files, parents=commit_parents,
                           is_merge_commit=commit_is_merge_commit)

        # Create GitContext info with the commit object and return

        context.commits.append(commit)
        return context

    def __eq__(self, other):
        return isinstance(other, GitContext) and self.commits == other.commits
