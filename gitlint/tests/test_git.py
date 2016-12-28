# -*- coding: utf-8 -*-

import datetime
import dateutil
from mock import patch, call
from sh import ErrorReturnCode, CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext, GitCommit, GitCommitMessage, GitContextError


class GitTests(BaseTestCase):
    @patch('gitlint.git.sh')
    def test_get_latest_commit(self, sh):
        def git_log_side_effect(*args, **_kwargs):
            return_values = {'--pretty=%B': u"cömmit-title\n\ncömmit-body", '--pretty=%aN': u"test åuthor",
                             '--pretty=%aE': u"test-emåil@foo.com", '--pretty=%ai': u"2016-12-03 15:28:15 01:00",
                             '--pretty=%P': u"åbc"}
            return return_values[args[1]]

        sh.git.log.side_effect = git_log_side_effect
        sh.git.return_value = u"file1.txt\npåth/to/file2.txt\n"

        context = GitContext.from_local_repository(u"fake/påth")
        expected_sh_special_args = {
            '_tty_out': False,
            '_cwd': u"fake/påth"
        }
        # assert that commit info was read using git command
        expected_calls = [call('-1', '--pretty=%B', _cwd=u"fake/påth", _tty_out=False),
                          call('-1', '--pretty=%aN', _cwd=u"fake/påth", _tty_out=False),
                          call('-1', '--pretty=%aE', _cwd=u"fake/påth", _tty_out=False),
                          call('-1', '--pretty=%ai', _cwd=u"fake/påth", _tty_out=False),
                          call('-1', '--pretty=%P', _cwd=u"fake/påth", _tty_out=False)]

        self.assertListEqual(sh.git.log.mock_calls, expected_calls)

        last_commit = context.commits[-1]
        self.assertEqual(last_commit.message.title, u"cömmit-title")
        self.assertEqual(last_commit.message.body, ["", u"cömmit-body"])
        self.assertEqual(last_commit.author_name, u"test åuthor")
        self.assertEqual(last_commit.author_email, u"test-emåil@foo.com")
        self.assertEqual(last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15,
                                                             tzinfo=dateutil.tz.tzoffset("+0100", 3600)))
        self.assertListEqual(last_commit.parents, [u"åbc"])
        self.assertFalse(last_commit.is_merge_commit)

        # assert that changed files are read using git command
        sh.git.assert_called_once_with('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD',
                                       **expected_sh_special_args)
        self.assertListEqual(last_commit.changed_files, ["file1.txt", u"påth/to/file2.txt"])

    @patch('gitlint.git.sh')
    def test_get_latest_commit_merge_commit(self, sh):
        def git_log_side_effect(*args, **_kwargs):
            return_values = {'--pretty=%B': u"Merge \"foo bår commit\"", '--pretty=%aN': u"test åuthor",
                             '--pretty=%aE': u"test-emåil@foo.com", '--pretty=%ai': u"2016-12-03 15:28:15 01:00",
                             '--pretty=%P': u"åbc def"}
            return return_values[args[1]]

        sh.git.log.side_effect = git_log_side_effect
        sh.git.return_value = u"file1.txt\npåth/to/file2.txt\n"

        context = GitContext.from_local_repository(u"fåke/path")
        expected_sh_special_args = {
            '_tty_out': False,
            '_cwd': u"fåke/path"
        }
        # assert that commit info was read using git command
        expected_calls = [call('-1', '--pretty=%B', _cwd=u"fåke/path", _tty_out=False),
                          call('-1', '--pretty=%aN', _cwd=u"fåke/path", _tty_out=False),
                          call('-1', '--pretty=%aE', _cwd=u"fåke/path", _tty_out=False),
                          call('-1', '--pretty=%ai', _cwd=u"fåke/path", _tty_out=False),
                          call('-1', '--pretty=%P', _cwd=u"fåke/path", _tty_out=False)]

        self.assertListEqual(sh.git.log.mock_calls, expected_calls)

        last_commit = context.commits[-1]
        self.assertEqual(last_commit.message.title, u"Merge \"foo bår commit\"")
        self.assertEqual(last_commit.message.body, [])
        self.assertEqual(last_commit.author_name, u"test åuthor")
        self.assertEqual(last_commit.author_email, u"test-emåil@foo.com")
        self.assertEqual(last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15,
                                                             tzinfo=dateutil.tz.tzoffset("+0100", 3600)))
        self.assertListEqual(last_commit.parents, [u"åbc", "def"])
        self.assertTrue(last_commit.is_merge_commit)

        # assert that changed files are read using git command
        sh.git.assert_called_once_with('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD',
                                       **expected_sh_special_args)
        self.assertListEqual(last_commit.changed_files, ["file1.txt", u"påth/to/file2.txt"])

    @patch('gitlint.git.sh')
    def test_get_latest_commit_command_not_found(self, sh):
        sh.git.log.side_effect = CommandNotFound("git")
        expected_msg = "'git' command not found. You need to install git to use gitlint on a local repository. " + \
                       "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
        with self.assertRaisesRegex(GitContextError, expected_msg):
            GitContext.from_local_repository(u"fåke/path")

        # assert that commit message was read using git command
        sh.git.log.assert_called_once_with('-1', '--pretty=%B', _tty_out=False, _cwd=u"fåke/path")

    @patch('gitlint.git.sh')
    def test_get_latest_commit_git_error(self, sh):
        # Current directory not a git repo
        err = b"fatal: Not a git repository (or any of the parent directories): .git"
        sh.git.log.side_effect = ErrorReturnCode("git log -1 --pretty=%B", b"", err)

        with self.assertRaisesRegex(GitContextError, u"fåke/path is not a git repository."):
            GitContext.from_local_repository(u"fåke/path")

        # assert that commit message was read using git command
        sh.git.log.assert_called_once_with('-1', '--pretty=%B', _tty_out=False, _cwd=u"fåke/path")

        sh.git.log.reset_mock()
        err = b"fatal: Random git error"
        sh.git.log.side_effect = ErrorReturnCode("git log -1 --pretty=%B", b"", err)

        expected_msg = u"An error occurred while executing 'git log -1 --pretty=%B': {0}".format(err)
        with self.assertRaisesRegex(GitContextError, expected_msg):
            GitContext.from_local_repository(u"fåke/path")

        # assert that commit message was read using git command
        sh.git.log.assert_called_once_with('-1', '--pretty=%B', _tty_out=False, _cwd=u"fåke/path")

    def test_from_commit_msg_full(self):
        gitcontext = GitContext.from_commit_msg(self.get_sample("commit_message/sample1"))

        expected_title = u"Commit title contåining 'WIP', as well as trailing punctuation."
        expected_body = ["This line should be empty",
                         "This is the first line of the commit message body and it is meant to test a " +
                         "line that exceeds the maximum line length of 80 characters.",
                         u"This line has a tråiling space. ",
                         "This line has a trailing tab.\t"]
        expected_full = expected_title + "\n" + "\n".join(expected_body)
        expected_original = expected_full + u"\n# This is a cömmented  line\n"

        commit = gitcontext.commits[-1]
        self.assertEqual(commit.message.title, expected_title)
        self.assertEqual(commit.message.body, expected_body)
        self.assertEqual(commit.message.full, expected_full)
        self.assertEqual(commit.message.original, expected_original)
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_just_title(self):
        gitcontext = GitContext.from_commit_msg(self.get_sample("commit_message/sample2"))
        commit = gitcontext.commits[-1]

        self.assertEqual(commit.message.title, u"Just a title contåining WIP")
        self.assertEqual(commit.message.body, [])
        self.assertEqual(commit.message.full, u"Just a title contåining WIP")
        self.assertEqual(commit.message.original, u"Just a title contåining WIP")
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertListEqual(commit.parents, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_empty(self):
        gitcontext = GitContext.from_commit_msg("")
        commit = gitcontext.commits[-1]

        self.assertEqual(commit.message.title, "")
        self.assertEqual(commit.message.body, [])
        self.assertEqual(commit.message.full, "")
        self.assertEqual(commit.message.original, "")
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_comment(self):
        gitcontext = GitContext.from_commit_msg(u"Tïtle\n\nBödy 1\n#Cömment\nBody 2")
        commit = gitcontext.commits[-1]

        self.assertEqual(commit.message.title, u"Tïtle")
        self.assertEqual(commit.message.body, ["", u"Bödy 1", "Body 2"])
        self.assertEqual(commit.message.full, u"Tïtle\n\nBödy 1\nBody 2")
        self.assertEqual(commit.message.original, u"Tïtle\n\nBödy 1\n#Cömment\nBody 2")
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_merge_commit(self):
        commit_msg = "Merge f919b8f34898d9b48048bcd703bc47139f4ff621 into 8b0409a26da6ba8a47c1fd2e746872a8dab15401"
        gitcontext = GitContext.from_commit_msg(commit_msg)
        commit = gitcontext.commits[-1]

        self.assertEqual(commit.message.title, commit_msg)
        self.assertEqual(commit.message.body, [])
        self.assertEqual(commit.message.full, commit_msg)
        self.assertEqual(commit.message.original, commit_msg)
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertTrue(commit.is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_gitcommit_equality(self):
        # Test simple equality case
        now = datetime.datetime.utcnow()
        context1 = GitContext()
        commit_message1 = GitCommitMessage(u"tëst\n\nfoo", u"tëst\n\nfoo", u"tēst", ["", u"föo"])
        commit1 = GitCommit(context1, commit_message1, now, u"Jöhn Smith", u"jöhn.smith@test.com", None, True,
                            [u"föo/bar"])
        context1.commits = [commit1]

        context2 = GitContext()
        commit_message2 = GitCommitMessage(u"tëst\n\nfoo", u"tëst\n\nfoo", u"tēst", ["", u"föo"])
        commit2 = GitCommit(context1, commit_message1, now, u"Jöhn Smith", u"jöhn.smith@test.com", None, True,
                            [u"föo/bar"])
        context2.commits = [commit2]

        self.assertEqual(context1, context2)
        self.assertEqual(commit_message1, commit_message2)
        self.assertEqual(commit1, commit2)

        # Check that objects are inequal when changing a single attribute
        for attr in ['message', 'author_name', 'author_email', 'parents', 'is_merge_commit', 'changed_files']:
            prev_val = getattr(commit1, attr)
            setattr(commit1, attr, u"föo")
            self.assertNotEqual(commit1, commit2)
            setattr(commit1, attr, prev_val)
            self.assertEqual(commit1, commit2)
