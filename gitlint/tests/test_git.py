from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext

from mock import patch


class GitTests(BaseTestCase):
    @patch('gitlint.git.sh')
    def test_get_latest_commit(self, sh):
        sh.git.log.return_value = "commit-title\n\ncommit-body"
        sh.git.return_value = "file1.txt\npath/to/file2.txt\n"

        context = GitContext.from_local_repository()

        # assert that commit message was read using git command
        sh.git.log.assert_called_once_with('-1', '--pretty=%B', _tty_out=False)
        self.assertEqual(context.commit_msg.title, "commit-title")
        self.assertEqual(context.commit_msg.body, ["", "commit-body"])

        # assert that changed files are read using git command
        sh.git.assert_called_once_with('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD', _tty_out=False)
        self.assertListEqual(context.changed_files, ["file1.txt", "path/to/file2.txt"])

    def test_set_commit_msg_full(self):
        gitcontext = GitContext()
        gitcontext.set_commit_msg(self.get_sample("commit_message/sample1"))

        expected_title = "Commit title containing 'WIP', as well as trailing punctuation."
        expected_body = ["This line should be empty",
                         "This is the first line of the commit message body and it is meant to test a " +
                         "line that exceeds the maximum line length of 80 characters.",
                         "This line has a trailing space. ",
                         "This line has a trailing tab.\t", ""]
        expected_full = expected_title + "\n" + "\n".join(expected_body)
        expected_original = expected_full + "# This is a commented  line\n"

        self.assertEqual(gitcontext.commit_msg.title, expected_title)
        self.assertEqual(gitcontext.commit_msg.body, expected_body)
        self.assertEqual(gitcontext.commit_msg.full, expected_full)
        self.assertEqual(gitcontext.commit_msg.original, expected_original)

    def test_set_commit_msg_just_title(self):
        gitcontext = GitContext()
        gitcontext.set_commit_msg(self.get_sample("commit_message/sample2"))

        self.assertEqual(gitcontext.commit_msg.title, "Just a title containing WIP")
        self.assertEqual(gitcontext.commit_msg.body, [])
        self.assertEqual(gitcontext.commit_msg.full, "Just a title containing WIP")
        self.assertEqual(gitcontext.commit_msg.original, "Just a title containing WIP")
