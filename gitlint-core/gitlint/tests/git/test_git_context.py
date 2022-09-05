from unittest.mock import patch, call

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext


class GitContextTests(BaseTestCase):
    # Expected special_args passed to 'sh'
    expected_sh_special_args = {"_tty_out": False, "_cwd": "fåke/path"}

    @patch("gitlint.git.sh")
    def test_gitcontext(self, sh):
        sh.git.side_effect = ["#", "\nfoöbar\n"]  # git config --get core.commentchar

        expected_calls = [
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call("rev-parse", "--abbrev-ref", "HEAD", **self.expected_sh_special_args),
        ]

        context = GitContext("fåke/path")
        self.assertEqual(sh.git.mock_calls, [])

        # gitcontext.comment_branch
        self.assertEqual(context.commentchar, "#")
        self.assertEqual(sh.git.mock_calls, expected_calls[0:1])

        # gitcontext.current_branch
        self.assertEqual(context.current_branch, "foöbar")
        self.assertEqual(sh.git.mock_calls, expected_calls)

    @patch("gitlint.git.sh")
    def test_gitcontext_equality(self, sh):
        sh.git.side_effect = [
            "û\n",  # context1: git config --get core.commentchar
            "û\n",  # context2: git config --get core.commentchar
            "my-brånch\n",  # context1: git rev-parse --abbrev-ref HEAD
            "my-brånch\n",  # context2: git rev-parse --abbrev-ref HEAD
        ]

        context1 = GitContext("fåke/path")
        context1.commits = ["fōo", "bår"]  # we don't need real commits to check for equality

        context2 = GitContext("fåke/path")
        context2.commits = ["fōo", "bår"]
        self.assertEqual(context1, context2)

        # INEQUALITY
        # Different commits
        context2.commits = ["hür", "dür"]
        self.assertNotEqual(context1, context2)

        # Different repository_path
        context2.commits = context1.commits
        context2.repository_path = "ōther/path"
        self.assertNotEqual(context1, context2)

        # Different comment_char
        context3 = GitContext("fåke/path")
        context3.commits = ["fōo", "bår"]
        sh.git.side_effect = [
            "ç\n",  # context3: git config --get core.commentchar
            "my-brånch\n",  # context3: git rev-parse --abbrev-ref HEAD
        ]
        self.assertNotEqual(context1, context3)

        # Different current_branch
        context4 = GitContext("fåke/path")
        context4.commits = ["fōo", "bår"]
        sh.git.side_effect = [
            "û\n",  # context4: git config --get core.commentchar
            "different-brånch\n",  # context4: git rev-parse --abbrev-ref HEAD
        ]
        self.assertNotEqual(context1, context4)
