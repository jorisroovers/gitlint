import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import arrow

from gitlint import shell as sh
from gitlint.cache import PropertyCache, cache
from gitlint.exception import GitlintError

# import exceptions separately, this makes it a little easier to mock them out in the unit tests
from gitlint.shell import CommandNotFound, ErrorReturnCode

# For now, the git date format we use is fixed, but technically this format is determined by `git config log.date`
# We should fix this at some point :-)
GIT_TIMEFORMAT = "YYYY-MM-DD HH:mm:ss Z"

LOG = logging.getLogger(__name__)


class GitContextError(GitlintError):
    """Exception indicating there is an issue with the git context"""


class GitNotInstalledError(GitContextError):
    def __init__(self):
        super().__init__(
            "'git' command not found. You need to install git to use gitlint on a local repository. "
            "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
        )


class GitExitCodeError(GitContextError):
    def __init__(self, command, stderr):
        self.command = command
        self.stderr = stderr
        super().__init__(f"An error occurred while executing '{command}': {stderr}")


def _git(*command_parts, **kwargs):
    """Convenience function for running git commands. Automatically deals with exceptions and unicode."""
    git_kwargs = {"_tty_out": False}
    git_kwargs.update(kwargs)
    try:
        LOG.debug(command_parts)
        result = sh.git(*command_parts, **git_kwargs)
        # If we reach this point and the result has an exit_code that is larger than 0, this means that we didn't
        # get an exception (which is the default sh behavior for non-zero exit codes) and so the user is expecting
        # a non-zero exit code -> just return the entire result
        if hasattr(result, "exit_code") and result.exit_code > 0:
            return result
        return str(result)
    except CommandNotFound as e:
        raise GitNotInstalledError from e
    except ErrorReturnCode as e:  # Something went wrong while executing the git command
        error_msg = e.stderr.strip()
        error_msg_lower = error_msg.lower()
        if "_cwd" in git_kwargs and b"not a git repository" in error_msg_lower:
            raise GitContextError(f"{git_kwargs['_cwd']} is not a git repository.") from e

        if (
            b"does not have any commits yet" in error_msg_lower
            or b"ambiguous argument 'head': unknown revision" in error_msg_lower
        ):
            msg = "Current branch has no commits. Gitlint requires at least one commit to function."
            raise GitContextError(msg) from e

        raise GitExitCodeError(e.full_cmd, error_msg) from e


def git_version():
    """Determine the git version installed on this host by calling git --version"""
    return _git("--version").replace("\n", "")


def git_commentchar(repository_path=None):
    """Shortcut for retrieving comment char from git config"""
    commentchar = _git("config", "--get", "core.commentchar", _cwd=repository_path, _ok_code=[0, 1])
    # git will return an exit code of 1 if it can't find a config value, in this case we fall-back to # as commentchar
    if hasattr(commentchar, "exit_code") and commentchar.exit_code == 1:
        commentchar = "#"
    return commentchar.replace("\n", "")


def git_hooks_dir(repository_path):
    """Determine hooks directory for a given target dir"""
    hooks_dir = _git("rev-parse", "--git-path", "hooks", _cwd=repository_path)
    hooks_dir = hooks_dir.replace("\n", "")
    return os.path.realpath(os.path.join(repository_path, hooks_dir))


def _parse_git_changed_file_stats(changed_files_stats_raw):
    """Parse the output of git diff --numstat and return a dict of:
    dict[filename: GitChangedFileStats(filename, additions, deletions)]"""
    changed_files_stats_lines = changed_files_stats_raw.split("\n")
    changed_files_stats = {}
    for line in changed_files_stats_lines[:-1]:  # drop last empty line
        line_stats = line.split()

        # If the file is binary, numstat will show "-"
        # See https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---numstat
        additions = int(line_stats[0]) if line_stats[0] != "-" else None
        deletions = int(line_stats[1]) if line_stats[1] != "-" else None

        changed_file_stat = GitChangedFileStats(line_stats[2], additions, deletions)
        changed_files_stats[line_stats[2]] = changed_file_stat

    return changed_files_stats


@dataclass
class GitContext(PropertyCache):
    """Class representing the git context in which gitlint is operating: a data object storing information about
    the git repository that gitlint is linting.
    """

    commits: List["GitCommit"] = field(init=False, default_factory=list)
    repository_path: Optional[str] = None

    @property
    @cache
    def commentchar(self):
        return git_commentchar(self.repository_path)

    @property
    @cache
    def current_branch(self):
        try:
            current_branch = _git("rev-parse", "--abbrev-ref", "HEAD", _cwd=self.repository_path).strip()
        except GitContextError:
            # Maybe there is no commit.  Try another way to get current branch (need Git 2.22+)
            current_branch = _git("branch", "--show-current", _cwd=self.repository_path).strip()
        return current_branch

    @staticmethod
    def from_commit_msg(commit_msg_str):
        """Determines git context based on a commit message.
        :param commit_msg_str: Full git commit message.
        """
        context = GitContext()
        commit_msg_obj = GitCommitMessage.from_full_message(context, commit_msg_str)
        commit = GitCommit(context, commit_msg_obj)
        context.commits.append(commit)
        return context

    @staticmethod
    def from_staged_commit(commit_msg_str, repository_path):
        """Determines git context based on a commit message that is a staged commit for a local git repository.
        :param commit_msg_str: Full git commit message.
        :param repository_path: Path to the git repository to retrieve the context from
        """
        context = GitContext(repository_path=repository_path)
        commit_msg_obj = GitCommitMessage.from_full_message(context, commit_msg_str)
        commit = StagedLocalGitCommit(context, commit_msg_obj)
        context.commits.append(commit)
        return context

    @staticmethod
    def from_local_repository(repository_path, refspec=None, commit_hashes=None):
        """Retrieves the git context from a local git repository.
        :param repository_path: Path to the git repository to retrieve the context from
        :param refspec: The commit(s) to retrieve (mutually exclusive with `commit_hash`)
        :param commit_hash: Hash of the commit to retrieve (mutually exclusive with `refspec`)
        """

        context = GitContext(repository_path=repository_path)

        if refspec:
            sha_list = _git("rev-list", refspec, _cwd=repository_path).split()
        elif commit_hashes:  # One or more commit hashes, just pass it to `git log -1`
            # Even though we have already been passed the commit hash, we ask git to retrieve this hash and
            # return it to us. This way we verify that the passed hash is a valid hash for the target repo and we
            # also convert it to the full hash format (we might have been passed a short hash).
            sha_list = []
            for commit_hash in commit_hashes:
                sha_list.append(_git("log", "-1", commit_hash, "--pretty=%H", _cwd=repository_path).replace("\n", ""))
        else:  # If no refspec is defined, fallback to the last commit on the current branch
            # We tried many things here e.g.: defaulting to e.g. HEAD or HEAD^... (incl. dealing with
            # repos that only have a single commit - HEAD^... doesn't work there), but then we still get into
            # problems with e.g. merge commits. Easiest solution is just taking the SHA from `git log -1`.
            sha_list = [_git("log", "-1", "--pretty=%H", _cwd=repository_path).replace("\n", "")]

        for sha in sha_list:
            commit = LocalGitCommit(context, sha)
            context.commits.append(commit)

        return context

    def __eq__(self, other):
        return (
            isinstance(other, GitContext)
            and self.commits == other.commits
            and self.repository_path == other.repository_path
            and self.commentchar == other.commentchar
            and self.current_branch == other.current_branch
        )


@dataclass
class GitCommitMessage:
    """Class representing a git commit message. A commit message consists of the following:
    - context: The `GitContext` this commit message is part of
    - original: The actual commit message as returned by `git log`
    - full: original, but stripped of any comments
    - title: the first line of full
    - body: all lines following the title
    """

    context: GitContext = field(compare=False)
    original: str
    full: str
    title: str
    body: List[str]

    @staticmethod
    def from_full_message(context, commit_msg_str):
        """Parses a full git commit message by parsing a given string into the different parts of a commit message"""
        all_lines = commit_msg_str.splitlines()
        cutline = f"{context.commentchar} ------------------------ >8 ------------------------"
        try:
            cutline_index = all_lines.index(cutline)
        except ValueError:
            cutline_index = None
        lines = [line for line in all_lines[:cutline_index] if not line.startswith(context.commentchar)]
        full = "\n".join(lines)
        title = lines[0] if lines else ""
        body = lines[1:] if len(lines) > 1 else []
        return GitCommitMessage(context=context, original=commit_msg_str, full=full, title=title, body=body)

    def __str__(self):
        return self.full


@dataclass
class GitChangedFileStats:
    """Class representing the stats for a changed file in git"""

    filepath: Path
    additions: int
    deletions: int

    def __str__(self) -> str:
        return f"{self.filepath}: {self.additions} additions, {self.deletions} deletions"


@dataclass
class GitCommit:
    """Class representing a git commit.
    A commit consists of: context, message, author name, author email, date, list of parent commit shas,
    list of changed files, list of branch names.
    In the context of gitlint, only the git context and commit message are required.
    """

    context: GitContext = field(compare=False)
    message: GitCommitMessage
    sha: Optional[str] = None
    date: Optional[datetime] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    parents: List[str] = field(default_factory=list)
    changed_files_stats: Dict[str, GitChangedFileStats] = field(default_factory=dict)
    branches: List[str] = field(default_factory=list)

    @property
    def is_merge_commit(self):
        return self.message.title.startswith("Merge")

    @property
    def is_fixup_commit(self):
        return self.message.title.startswith("fixup!")

    @property
    def is_squash_commit(self):
        return self.message.title.startswith("squash!")

    @property
    def is_fixup_amend_commit(self):
        return self.message.title.startswith("amend!")

    @property
    def is_revert_commit(self):
        return self.message.title.startswith("Revert")

    @property
    def changed_files(self):
        return list(self.changed_files_stats.keys())

    def __str__(self):
        date_str = arrow.get(self.date).format(GIT_TIMEFORMAT) if self.date else None

        if len(self.changed_files_stats) > 0:
            changed_files_stats_str = "\n  " + "\n  ".join([str(stats) for stats in self.changed_files_stats.values()])
        else:
            changed_files_stats_str = " {}"

        return (
            f"--- Commit Message ----\n{self.message}\n"
            "--- Meta info ---------\n"
            f"Author: {self.author_name} <{self.author_email}>\n"
            f"Date:   {date_str}\n"
            f"is-merge-commit:  {self.is_merge_commit}\n"
            f"is-fixup-commit:  {self.is_fixup_commit}\n"
            f"is-fixup-amend-commit: {self.is_fixup_amend_commit}\n"
            f"is-squash-commit: {self.is_squash_commit}\n"
            f"is-revert-commit: {self.is_revert_commit}\n"
            f"Parents: {self.parents}\n"
            f"Branches: {self.branches}\n"
            f"Changed Files: {self.changed_files}\n"
            f"Changed Files Stats:{changed_files_stats_str}\n"
            "-----------------------"
        )


@dataclass
class LocalGitCommit(GitCommit, PropertyCache):
    """Class representing a git commit that exists in the local git repository.
    This class uses lazy loading: it defers reading information from the local git repository until the associated
    property is accessed for the first time. Properties are then cached for subsequent access.

    This approach ensures that we don't do 'expensive' git calls when certain properties are not actually used.
    In addition, reading the required info when it's needed rather than up front avoids adding delay during gitlint
    startup time and reduces gitlint's memory footprint.
    """

    def __init__(self, context, sha):
        PropertyCache.__init__(self)
        self.context = context
        self.sha = sha

    def _log(self):
        """Does a call to `git log` to determine a bunch of information about the commit."""
        long_format = "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B"
        raw_commit = _git("log", self.sha, "-1", long_format, _cwd=self.context.repository_path).split("\n")

        (name, email, date, parents), commit_msg = raw_commit[0].split("\x00"), "\n".join(raw_commit[1:])

        commit_parents = [] if parents == "" else parents.split(" ")
        commit_is_merge_commit = len(commit_parents) > 1

        # "YYYY-MM-DD HH:mm:ss Z" -> ISO 8601-like format
        # Use arrow for datetime parsing, because apparently python is quirky around ISO-8601 dates:
        # http://stackoverflow.com/a/30696682/381010
        commit_date = arrow.get(date, GIT_TIMEFORMAT).datetime

        # Create Git commit object with the retrieved info
        commit_msg_obj = GitCommitMessage.from_full_message(self.context, commit_msg)

        self._cache.update(
            {
                "message": commit_msg_obj,
                "author_name": name,
                "author_email": email,
                "date": commit_date,
                "parents": commit_parents,
                "is_merge_commit": commit_is_merge_commit,
            }
        )

    @property
    def message(self):
        return self._try_cache("message", self._log)

    @property
    def author_name(self):
        return self._try_cache("author_name", self._log)

    @property
    def author_email(self):
        return self._try_cache("author_email", self._log)

    @property
    def date(self):
        return self._try_cache("date", self._log)

    @property
    def parents(self):
        return self._try_cache("parents", self._log)

    @property
    def branches(self):
        def cache_branches():
            # We have to parse 'git branch --contains <sha>' instead of 'git for-each-ref' to be compatible with
            # git versions < 2.7.0
            # https://stackoverflow.com/questions/45173979/can-i-force-git-branch-contains-tag-to-not-print-the-asterisk
            branches = _git("branch", "--contains", self.sha, _cwd=self.context.repository_path).split("\n")

            # This means that we need to remove any leading * that indicates the current branch. Note that we can
            # safely do this since git branches cannot contain '*' anywhere, so if we find an '*' we know it's output
            # from the git CLI and not part of the branch name. See https://git-scm.com/docs/git-check-ref-format
            # We also drop the last empty line from the output.
            self._cache["branches"] = [branch.replace("*", "").strip() for branch in branches[:-1]]

        return self._try_cache("branches", cache_branches)

    @property
    def is_merge_commit(self):
        return self._try_cache("is_merge_commit", self._log)

    @property
    def changed_files_stats(self):
        def cache_changed_files_stats():
            changed_files_stats_raw = _git(
                "diff-tree", "--no-commit-id", "--numstat", "-r", "--root", self.sha, _cwd=self.context.repository_path
            )
            self._cache["changed_files_stats"] = _parse_git_changed_file_stats(changed_files_stats_raw)

        return self._try_cache("changed_files_stats", cache_changed_files_stats)


@dataclass
class StagedLocalGitCommit(GitCommit, PropertyCache):
    """Class representing a git commit that has been staged, but not committed.

    Other than the commit message itself (and changed files), a lot of information is actually not known at staging
    time, since the commit hasn't happened yet. However, we can make educated guesses based on existing repository
    information.
    """

    def __init__(self, context, commit_message):
        PropertyCache.__init__(self)
        self.context = context
        self.message = commit_message
        self.sha = None
        self.parents = []  # Not really possible to determine before a commit

    @property
    @cache
    def author_name(self):
        try:
            return _git("config", "--get", "user.name", _cwd=self.context.repository_path).strip()
        except GitExitCodeError as e:
            raise GitContextError("Missing git configuration: please set user.name") from e

    @property
    @cache
    def author_email(self):
        try:
            return _git("config", "--get", "user.email", _cwd=self.context.repository_path).strip()
        except GitExitCodeError as e:
            raise GitContextError("Missing git configuration: please set user.email") from e

    @property
    @cache
    def date(self):
        # We don't know the actual commit date yet, but we make a pragmatic trade-off here by providing the current date
        # We get current date from arrow, reformat in git date format, then re-interpret it as a date.
        # This ensure we capture the same precision and timezone information that git does.
        return arrow.get(arrow.now().format(GIT_TIMEFORMAT), GIT_TIMEFORMAT).datetime

    @property
    @cache
    def branches(self):
        # We don't know the branch this commit will be part of yet, but we're pragmatic here and just return the
        # current branch, as for all intents and purposes, this will be what the user is looking for.
        return [self.context.current_branch]

    @property
    def changed_files_stats(self):
        def cache_changed_files_stats():
            changed_files_stats_raw = _git("diff", "--staged", "--numstat", "-r", _cwd=self.context.repository_path)
            self._cache["changed_files_stats"] = _parse_git_changed_file_stats(changed_files_stats_raw)

        return self._try_cache("changed_files_stats", cache_changed_files_stats)
