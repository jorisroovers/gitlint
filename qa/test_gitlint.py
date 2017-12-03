# -*- coding: utf-8 -*-

import os
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
        hash = self.get_last_commit_hash()

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

    def test_fixup_commit(self):
        # Create a normal commit and assert that it has a violation
        test_filename = self._create_simple_commit(u"Cömmit on WIP master\n\nSimple bödy that is long enough")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"Cömmit on WIP master\"\n"
        self.assertEqual(output, expected)

        # Make a small modification to the commit and commit it using fixup commit
        with open(os.path.join(self.tmp_git_repo, test_filename), "a") as fh:
            # Wanted to write a unicode string, but that's obnoxious if you want to do it across Python 2 and 3.
            # https://stackoverflow.com/questions/22392377/
            # error-writing-a-file-with-file-write-in-python-unicodeencodeerror
            # So just keeping it simple - ASCII will here
            fh.write("Appending some stuff\n")

        git("add", test_filename, _cwd=self.tmp_git_repo)

        git("commit", "--fixup", self.get_last_commit_hash(), _cwd=self.tmp_git_repo)

        # Assert that gitlint does not show an error for the fixup commit
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        # No need to check exit code, the command above throws an exception on > 0 exit codes
        self.assertEqual(output, "")

        # Make sure that if we set the ignore-fixup-commits option to false that we do still see the violations
        output = gitlint("-c", "general.ignore-fixup-commits=false", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"fixup! Cömmit on WIP master\"\n" + \
            u"3: B6 Body message is missing\n"

        self.assertEqual(output, expected)

    def test_squash_commit(self):
        # Create a normal commit and assert that it has a violation
        test_filename = self._create_simple_commit(u"Cömmit on WIP master\n\nSimple bödy that is long enough")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"Cömmit on WIP master\"\n"
        self.assertEqual(output, expected)

        # Make a small modification to the commit and commit it using squash commit
        with open(os.path.join(self.tmp_git_repo, test_filename), "a") as fh:
            # Wanted to write a unicode string, but that's obnoxious if you want to do it across Python 2 and 3.
            # https://stackoverflow.com/questions/22392377/
            # error-writing-a-file-with-file-write-in-python-unicodeencodeerror
            # So just keeping it simple - ASCII will here
            fh.write("Appending some stuff\n")

        git("add", test_filename, _cwd=self.tmp_git_repo)

        git("commit", "--squash", self.get_last_commit_hash(), "-m", u"Töo short body", _cwd=self.tmp_git_repo)

        # Assert that gitlint does not show an error for the fixup commit
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        # No need to check exit code, the command above throws an exception on > 0 exit codes
        self.assertEqual(output, "")

        # Make sure that if we set the ignore-squash-commits option to false that we do still see the violations
        output = gitlint("-c", "general.ignore-squash-commits=false",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"squash! Cömmit on WIP master\"\n" + \
            u"3: B5 Body message is too short (14<20): \"Töo short body\"\n"

        self.assertEqual(output, expected)

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
