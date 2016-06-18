from mock import patch, call
from sh import ErrorReturnCode, CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext, GitContextError


class GitTests(BaseTestCase):
    @patch('gitlint.git.sh')
    def test_get_latest_commit(self, sh):
        def git_log_side_effect(*args, **_kwargs):
            return_values = {'--pretty=%B': "commit-title\n\ncommit-body", '--pretty=%aN': "test author",
                             '--pretty=%aE': "test-email@foo.com", '--pretty=%aD': "Mon Feb 29 22:19:39 2016 +0100",
                             '--pretty=%P': "abc"}
            return return_values[args[1]]

        sh.git.log.side_effect = git_log_side_effect
        sh.git.return_value = "file1.txt\npath/to/file2.txt\n"

        context = GitContext.from_local_repository("fake/path")
        expected_sh_special_args = {
            '_tty_out': False,
            '_cwd': "fake/path"
        }
        # assert that commit info was read using git command
        expected_calls = [call('-1', '--pretty=%B', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%aN', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%aE', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%aD', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%P', _cwd='fake/path', _tty_out=False)]

        self.assertListEqual(sh.git.log.mock_calls, expected_calls)

        last_commit = context.commits[-1]
        self.assertEqual(last_commit.message.title, "commit-title")
        self.assertEqual(last_commit.message.body, ["", "commit-body"])
        self.assertEqual(last_commit.author_name, "test author")
        self.assertEqual(last_commit.author_email, "test-email@foo.com")
        self.assertListEqual(last_commit.parents, ["abc"])
        self.assertFalse(last_commit.is_merge_commit)

        # assert that changed files are read using git command
        sh.git.assert_called_once_with('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD',
                                       **expected_sh_special_args)
        self.assertListEqual(last_commit.changed_files, ["file1.txt", "path/to/file2.txt"])

    @patch('gitlint.git.sh')
    def test_get_latest_commit_merge_commit(self, sh):
        def git_log_side_effect(*args, **_kwargs):
            return_values = {'--pretty=%B': "Merge \"foo bar commit\"", '--pretty=%aN': "test author",
                             '--pretty=%aE': "test-email@foo.com", '--pretty=%aD': "Mon Feb 29 22:19:39 2016 +0100",
                             '--pretty=%P': "abc def"}
            return return_values[args[1]]

        sh.git.log.side_effect = git_log_side_effect
        sh.git.return_value = "file1.txt\npath/to/file2.txt\n"

        context = GitContext.from_local_repository("fake/path")
        expected_sh_special_args = {
            '_tty_out': False,
            '_cwd': "fake/path"
        }
        # assert that commit info was read using git command
        expected_calls = [call('-1', '--pretty=%B', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%aN', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%aE', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%aD', _cwd='fake/path', _tty_out=False),
                          call('-1', '--pretty=%P', _cwd='fake/path', _tty_out=False)]

        self.assertListEqual(sh.git.log.mock_calls, expected_calls)

        last_commit = context.commits[-1]
        self.assertEqual(last_commit.message.title, "Merge \"foo bar commit\"")
        self.assertEqual(last_commit.message.body, [])
        self.assertEqual(last_commit.author_name, "test author")
        self.assertEqual(last_commit.author_email, "test-email@foo.com")
        self.assertListEqual(last_commit.parents, ["abc", "def"])
        self.assertTrue(last_commit.is_merge_commit)

        # assert that changed files are read using git command
        sh.git.assert_called_once_with('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD',
                                       **expected_sh_special_args)
        self.assertListEqual(last_commit.changed_files, ["file1.txt", "path/to/file2.txt"])

    @patch('gitlint.git.sh')
    def test_get_latest_commit_command_not_found(self, sh):
        sh.git.log.side_effect = CommandNotFound("git")
        expected_msg = "'git' command not found. You need to install git to use gitlint on a local repository. " + \
                       "See https://git-scm.com/book/en/v2/Getting-Started-Installing-Git on how to install git."
        with self.assertRaisesRegexp(GitContextError, expected_msg):
            GitContext.from_local_repository("fake/path")

        # assert that commit message was read using git command
        sh.git.log.assert_called_once_with('-1', '--pretty=%B', _tty_out=False, _cwd="fake/path")

    @patch('gitlint.git.sh')
    def test_get_latest_commit_git_error(self, sh):
        err = b"fatal: Not a git repository (or any of the parent directories): .git"
        sh.git.log.side_effect = ErrorReturnCode("git log -1 --pretty=%B", b"", err)

        with self.assertRaisesRegexp(GitContextError, "fake/path is not a git repository."):
            GitContext.from_local_repository("fake/path")

        # assert that commit message was read using git command
        sh.git.log.assert_called_once_with('-1', '--pretty=%B', _tty_out=False, _cwd="fake/path")

    def test_from_commit_msg_full(self):
        gitcontext = GitContext.from_commit_msg(self.get_sample("commit_message/sample1"))

        expected_title = "Commit title containing 'WIP', as well as trailing punctuation."
        expected_body = ["This line should be empty",
                         "This is the first line of the commit message body and it is meant to test a " +
                         "line that exceeds the maximum line length of 80 characters.",
                         "This line has a trailing space. ",
                         "This line has a trailing tab.\t"]
        expected_full = expected_title + "\n" + "\n".join(expected_body)
        expected_original = expected_full + "\n# This is a commented  line\n"

        self.assertEqual(gitcontext.commits[-1].message.title, expected_title)
        self.assertEqual(gitcontext.commits[-1].message.body, expected_body)
        self.assertEqual(gitcontext.commits[-1].message.full, expected_full)
        self.assertEqual(gitcontext.commits[-1].message.original, expected_original)
        self.assertEqual(gitcontext.commits[-1].author_name, None)
        self.assertEqual(gitcontext.commits[-1].author_email, None)
        self.assertListEqual(gitcontext.commits[-1].parents, [])
        self.assertFalse(gitcontext.commits[-1].is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_just_title(self):
        gitcontext = GitContext.from_commit_msg(self.get_sample("commit_message/sample2"))

        self.assertEqual(gitcontext.commits[-1].message.title, "Just a title containing WIP")
        self.assertEqual(gitcontext.commits[-1].message.body, [])
        self.assertEqual(gitcontext.commits[-1].message.full, "Just a title containing WIP")
        self.assertEqual(gitcontext.commits[-1].message.original, "Just a title containing WIP")
        self.assertEqual(gitcontext.commits[-1].author_name, None)
        self.assertEqual(gitcontext.commits[-1].author_email, None)
        self.assertListEqual(gitcontext.commits[-1].parents, [])
        self.assertFalse(gitcontext.commits[-1].is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_empty(self):
        gitcontext = GitContext.from_commit_msg("")

        self.assertEqual(gitcontext.commits[-1].message.title, "")
        self.assertEqual(gitcontext.commits[-1].message.body, [])
        self.assertEqual(gitcontext.commits[-1].message.full, "")
        self.assertEqual(gitcontext.commits[-1].message.original, "")
        self.assertEqual(gitcontext.commits[-1].author_name, None)
        self.assertEqual(gitcontext.commits[-1].author_email, None)
        self.assertListEqual(gitcontext.commits[-1].parents, [])
        self.assertFalse(gitcontext.commits[-1].is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_comment(self):
        gitcontext = GitContext.from_commit_msg("Title\n\nBody 1\n#Comment\nBody 2")

        self.assertEqual(gitcontext.commits[-1].message.title, "Title")
        self.assertEqual(gitcontext.commits[-1].message.body, ["", "Body 1", "Body 2"])
        self.assertEqual(gitcontext.commits[-1].message.full, "Title\n\nBody 1\nBody 2")
        self.assertEqual(gitcontext.commits[-1].message.original, "Title\n\nBody 1\n#Comment\nBody 2")
        self.assertEqual(gitcontext.commits[-1].author_name, None)
        self.assertEqual(gitcontext.commits[-1].author_email, None)
        self.assertListEqual(gitcontext.commits[-1].parents, [])
        self.assertFalse(gitcontext.commits[-1].is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_merge_commit(self):
        commit_msg = "Merge f919b8f34898d9b48048bcd703bc47139f4ff621 into 8b0409a26da6ba8a47c1fd2e746872a8dab15401"
        gitcontext = GitContext.from_commit_msg(commit_msg)

        self.assertEqual(gitcontext.commits[-1].message.title, commit_msg)
        self.assertEqual(gitcontext.commits[-1].message.body, [])
        self.assertEqual(gitcontext.commits[-1].message.full, commit_msg)
        self.assertEqual(gitcontext.commits[-1].message.original, commit_msg)
        self.assertEqual(gitcontext.commits[-1].author_name, None)
        self.assertEqual(gitcontext.commits[-1].author_email, None)
        self.assertListEqual(gitcontext.commits[-1].parents, [])
        self.assertTrue(gitcontext.commits[-1].is_merge_commit)
        self.assertEqual(len(gitcontext.commits), 1)
