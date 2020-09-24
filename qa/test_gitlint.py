# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
import io
import os
from qa.shell import echo, git, gitlint
from qa.base import BaseTestCase
from qa.utils import DEFAULT_ENCODING


class IntegrationTests(BaseTestCase):
    """ Simple set of integration tests for gitlint """

    def test_successful(self):
        # Test for STDIN with and without a TTY attached
        self.create_simple_commit(u"Sïmple title\n\nSimple bödy describing the commit")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _err_to_out=True)
        self.assertEqualStdout(output, "")

    def test_successful_gitconfig(self):
        """ Test gitlint when the underlying repo has specific git config set.
        In the past, we've had issues with gitlint failing on some of these, so this acts as a regression test. """

        # Different commentchar (Note: tried setting this to a special unicode char, but git doesn't like that)
        git("config", "--add", "core.commentchar", "$", _cwd=self.tmp_git_repo)
        self.create_simple_commit(u"Sïmple title\n\nSimple bödy describing the commit\n$after commentchar\t ignored")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _err_to_out=True)
        self.assertEqualStdout(output, "")

    def test_successful_merge_commit(self):
        # Create branch on master
        self.create_simple_commit(u"Cömmit on master\n\nSimple bödy")

        # Create test branch, add a commit and determine the commit hash
        git("checkout", "-b", "test-branch", _cwd=self.tmp_git_repo)
        git("checkout", "test-branch", _cwd=self.tmp_git_repo)
        commit_title = u"Commit on test-brånch with a pretty long title that will cause issues when merging"
        self.create_simple_commit(u"{0}\n\nSïmple body".format(commit_title))
        hash = self.get_last_commit_hash()

        # Checkout master and merge the commit
        # We explicitly set the title of the merge commit to the title of the previous commit as this or similar
        # behavior is what many tools do that handle merges (like github, gerrit, etc).
        git("checkout", "master", _cwd=self.tmp_git_repo)
        git("merge", "--no-ff", "-m", u"Merge '{0}'".format(commit_title), hash, _cwd=self.tmp_git_repo)

        # Run gitlint and assert output is empty
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqualStdout(output, "")

        # Assert that we do see the error if we disable the ignore-merge-commits option
        output = gitlint("-c", "general.ignore-merge-commits=false", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        self.assertEqual(output.exit_code, 1)
        self.assertEqualStdout(output,
                               u"1: T1 Title exceeds max length (90>72): \"Merge '{0}'\"\n".format(commit_title))

    def test_fixup_commit(self):
        # Create a normal commit and assert that it has a violation
        test_filename = self.create_simple_commit(u"Cömmit on WIP master\n\nSimple bödy that is long enough")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"Cömmit on WIP master\"\n"
        self.assertEqualStdout(output, expected)

        # Make a small modification to the commit and commit it using fixup commit
        with io.open(os.path.join(self.tmp_git_repo, test_filename), "a", encoding=DEFAULT_ENCODING) as fh:
            # Wanted to write a unicode string, but that's obnoxious if you want to do it across Python 2 and 3.
            # https://stackoverflow.com/questions/22392377/
            # error-writing-a-file-with-file-write-in-python-unicodeencodeerror
            # So just keeping it simple - ASCII will here
            fh.write(u"Appending some stuff\n")

        git("add", test_filename, _cwd=self.tmp_git_repo)

        git("commit", "--fixup", self.get_last_commit_hash(), _cwd=self.tmp_git_repo)

        # Assert that gitlint does not show an error for the fixup commit
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        # No need to check exit code, the command above throws an exception on > 0 exit codes
        self.assertEqualStdout(output, "")

        # Make sure that if we set the ignore-fixup-commits option to false that we do still see the violations
        output = gitlint("-c", "general.ignore-fixup-commits=false", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"fixup! Cömmit on WIP master\"\n" + \
            u"3: B6 Body message is missing\n"

        self.assertEqualStdout(output, expected)

    def test_revert_commit(self):
        self.create_simple_commit(u"WIP: Cömmit on master.\n\nSimple bödy")
        hash = self.get_last_commit_hash()
        git("revert", hash, _cwd=self.tmp_git_repo)

        # Run gitlint and assert output is empty
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqualStdout(output, "")

        # Assert that we do see the error if we disable the ignore-revert-commits option
        output = gitlint("-c", "general.ignore-revert-commits=false",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        self.assertEqual(output.exit_code, 1)
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"Revert \"WIP: Cömmit on master.\"\"\n"
        self.assertEqualStdout(output, expected)

    def test_squash_commit(self):
        # Create a normal commit and assert that it has a violation
        test_filename = self.create_simple_commit(u"Cömmit on WIP master\n\nSimple bödy that is long enough")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"Cömmit on WIP master\"\n"
        self.assertEqualStdout(output, expected)

        # Make a small modification to the commit and commit it using squash commit
        with io.open(os.path.join(self.tmp_git_repo, test_filename), "a", encoding=DEFAULT_ENCODING) as fh:
            # Wanted to write a unicode string, but that's obnoxious if you want to do it across Python 2 and 3.
            # https://stackoverflow.com/questions/22392377/
            # error-writing-a-file-with-file-write-in-python-unicodeencodeerror
            # So just keeping it simple - ASCII will here
            fh.write(u"Appending some stuff\n")

        git("add", test_filename, _cwd=self.tmp_git_repo)

        git("commit", "--squash", self.get_last_commit_hash(), "-m", u"Töo short body", _cwd=self.tmp_git_repo)

        # Assert that gitlint does not show an error for the fixup commit
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        # No need to check exit code, the command above throws an exception on > 0 exit codes
        self.assertEqualStdout(output, "")

        # Make sure that if we set the ignore-squash-commits option to false that we do still see the violations
        output = gitlint("-c", "general.ignore-squash-commits=false",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"squash! Cömmit on WIP master\"\n" + \
            u"3: B5 Body message is too short (14<20): \"Töo short body\"\n"

        self.assertEqualStdout(output, expected)

    def test_violations(self):
        commit_msg = u"WIP: This ïs a title.\nContent on the sëcond line"
        self.create_simple_commit(commit_msg)
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqualStdout(output, self.get_expected("test_gitlint/test_violations_1"))

    def test_msg_filename(self):
        tmp_commit_msg_file = self.create_tmpfile(u"WIP: msg-fïlename test.")
        output = gitlint("--msg-filename", tmp_commit_msg_file, _tty_in=True, _ok_code=[3])
        self.assertEqualStdout(output, self.get_expected("test_gitlint/test_msg_filename_1"))

    def test_msg_filename_no_tty(self):
        """ Make sure --msg-filename option also works with no TTY attached """
        tmp_commit_msg_file = self.create_tmpfile(u"WIP: msg-fïlename NO TTY test.")

        # We need to set _err_to_out explicitly for sh to merge stdout and stderr output in case there's
        # no TTY attached to STDIN
        # http://amoffat.github.io/sh/sections/special_arguments.html?highlight=_tty_in#err-to-out
        # We need to pass some whitespace to _in as sh will otherwise hang, see
        # https://github.com/amoffat/sh/issues/427
        output = gitlint("--msg-filename", tmp_commit_msg_file, _in=" ",
                         _tty_in=False, _err_to_out=True, _ok_code=[3])

        self.assertEqualStdout(output, self.get_expected("test_gitlint/test_msg_filename_no_tty_1"))

    def test_no_git_name_set(self):
        """ Ensure we print out a helpful message if user.name is not set """
        tmp_commit_msg_file = self.create_tmpfile(u"WIP: msg-fïlename NO name test.")
        # Name is checked before email so this isn't strictly
        # necessary but seems good for consistency.
        env = self.create_tmp_git_config(u"[user]\n  email = test-emåil@foo.com\n")
        output = gitlint("--staged", "--msg-filename", tmp_commit_msg_file,
                         _ok_code=[self.GIT_CONTEXT_ERROR_CODE],
                         _env=env)
        expected = u"Missing git configuration: please set user.name\n"
        self.assertEqualStdout(output, expected)

    def test_no_git_email_set(self):
        """ Ensure we print out a helpful message if user.email is not set """
        tmp_commit_msg_file = self.create_tmpfile(u"WIP: msg-fïlename NO email test.")
        env = self.create_tmp_git_config(u"[user]\n  name = test åuthor\n")
        output = gitlint("--staged", "--msg-filename", tmp_commit_msg_file,
                         _ok_code=[self.GIT_CONTEXT_ERROR_CODE],
                         _env=env)
        expected = u"Missing git configuration: please set user.email\n"
        self.assertEqualStdout(output, expected)

    def test_git_errors(self):
        # Repo has no commits: caused by `git log`
        empty_git_repo = self.create_tmp_git_repo()
        output = gitlint(_cwd=empty_git_repo, _tty_in=True, _ok_code=[self.GIT_CONTEXT_ERROR_CODE])

        expected = u"Current branch has no commits. Gitlint requires at least one commit to function.\n"
        self.assertEqualStdout(output, expected)

        # Repo has no commits: caused by `git rev-parse`
        output = gitlint(echo(u"WIP: Pïpe test."), "--staged", _cwd=empty_git_repo, _tty_in=False,
                         _err_to_out=True, _ok_code=[self.GIT_CONTEXT_ERROR_CODE])
        self.assertEqualStdout(output, expected)
