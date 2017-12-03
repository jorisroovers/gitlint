# -*- coding: utf-8 -*-

from sh import git, gitlint, echo  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class IntegrationTests(BaseTestCase):
    """ Simple set of integration tests for gitlint """

    def test_successful(self):
        # Test for STDIN with and without a TTY attached
        for has_tty in [True, False]:
            self._create_simple_commit(u"Sïmple title\n\nSimple bödy describing the commit")
            output = gitlint(_cwd=self.tmp_git_repo, _tty_in=has_tty, _err_to_out=True)
            self.assertEqual(output, "")

    def test_successful_merge_commit(self):
        # Create branch on master
        self._create_simple_commit(u"Cömmit on master\n\nSimple bödy")

        # Create test branch, add a commit and determine the commit hash
        git("checkout", "-b", "test-branch", _cwd=self.tmp_git_repo)
        git("checkout", "test-branch", _cwd=self.tmp_git_repo)
        commit_title = u"Commit on test-brånch with a pretty long title that will cause issues when merging"
        self._create_simple_commit(u"{0}\n\nSïmple body".format(commit_title))
        hash = git("rev-parse", "HEAD", _cwd=self.tmp_git_repo, _tty_in=True).replace("\n", "")

        # Checkout master and merge the commit
        # We explicitly set the title of the merge commit to the title of the previous commit as this or similar
        # behavior is what many tools do that handle merges (like github, gerrit, etc).
        git("checkout", "master", _cwd=self.tmp_git_repo)
        git("merge", "--no-ff", "-m", u"Merge '{0}'".format(commit_title), hash, _cwd=self.tmp_git_repo)

        # Run gitlint and assert output is empty
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqual(output, "")

        # Assert that we do see the error if we disable the ignore-merge-commits option
        output = gitlint("-c", "general.ignore-merge-commits=false", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        self.assertEqual(output.exit_code, 1)
        self.assertEqual(output, u"1: T1 Title exceeds max length (90>72): \"Merge '{0}'\"\n".format(commit_title))

    def test_violations(self):
        # Test for STDIN with and without a TTY attached
        for has_tty in [True, False]:
            commit_msg = u"WIP: This ïs a title.\nContent on the sëcond line"
            self._create_simple_commit(commit_msg)
            # We need to set _err_to_out explicitly for sh to merge stdout and stderr output in case there's
            # no TTY attached to STDIN
            # http://amoffat.github.io/sh/sections/special_arguments.html?highlight=_tty_in#err-to-out
            output = gitlint(_cwd=self.tmp_git_repo, _tty_in=has_tty, _err_to_out=True, _ok_code=[3])

            expected = u"1: T3 Title has trailing punctuation (.): \"WIP: This ïs a title.\"\n" + \
                       u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: This ïs a title.\"\n" + \
                       u"2: B4 Second line is not empty: \"Content on the sëcond line\"\n"
            self.assertEqual(output, expected)

    def test_pipe_input(self):
        # NOTE: There is no use in testing this with _tty_in=True, because if you pipe something into a command
        # there never is a TTY connected to stdin (per definition).
        output = gitlint(echo(u"WIP: Pïpe test."), _tty_in=False, _err_to_out=True, _ok_code=[3])

        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Pïpe test.\"\n" + \
                   u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Pïpe test.\"\n" + \
                   u"3: B6 Body message is missing\n"

        self.assertEqual(output, expected)
