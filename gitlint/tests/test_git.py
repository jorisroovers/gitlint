from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext


class GitTests(BaseTestCase):
    def test_get_latest_commit(self):
        # Some issues with mocking out the 'sh' library. Need to investigate this further.
        pass

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
