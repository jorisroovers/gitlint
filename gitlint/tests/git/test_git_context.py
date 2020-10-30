# -*- coding: utf-8 -*-

from unittest.mock import patch, call

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext


class GitContextTests(BaseTestCase):

    # Expected special_args passed to 'sh'
    expected_sh_special_args = {
        '_tty_out': False,
        '_cwd': u"fåke/path"
    }

    @patch('gitlint.git.sh')
    def test_gitcontext(self, sh):

        sh.git.side_effect = [
            u"#",  # git config --get core.commentchar
            u"\nfoöbar\n"
        ]

        expected_calls = [
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call("rev-parse", "--abbrev-ref", "HEAD", **self.expected_sh_special_args)
        ]

        context = GitContext(u"fåke/path")
        self.assertEqual(sh.git.mock_calls, [])

        # gitcontext.comment_branch
        self.assertEqual(context.commentchar, u"#")
        self.assertEqual(sh.git.mock_calls, expected_calls[0:1])

        # gitcontext.current_branch
        self.assertEqual(context.current_branch, u"foöbar")
        self.assertEqual(sh.git.mock_calls, expected_calls)

    @patch('gitlint.git.sh')
    def test_gitcontext_equality(self, sh):

        sh.git.side_effect = [
            u"û\n",          # context1: git config --get core.commentchar
            u"û\n",          # context2: git config --get core.commentchar
            u"my-brånch\n",  # context1: git rev-parse --abbrev-ref HEAD
            u"my-brånch\n",  # context2: git rev-parse --abbrev-ref HEAD
        ]

        context1 = GitContext(u"fåke/path")
        context1.commits = [u"fōo", u"bår"]  # we don't need real commits to check for equality

        context2 = GitContext(u"fåke/path")
        context2.commits = [u"fōo", u"bår"]
        self.assertEqual(context1, context2)

        # INEQUALITY
        # Different commits
        context2.commits = [u"hür", u"dür"]
        self.assertNotEqual(context1, context2)

        # Different repository_path
        context2.commits = context1.commits
        context2.repository_path = u"ōther/path"
        self.assertNotEqual(context1, context2)

        # Different comment_char
        context3 = GitContext(u"fåke/path")
        context3.commits = [u"fōo", u"bår"]
        sh.git.side_effect = ([
            u"ç\n",                      # context3: git config --get core.commentchar
            u"my-brånch\n"               # context3: git rev-parse --abbrev-ref HEAD
        ])
        self.assertNotEqual(context1, context3)

        # Different current_branch
        context4 = GitContext(u"fåke/path")
        context4.commits = [u"fōo", u"bår"]
        sh.git.side_effect = ([
            u"û\n",                      # context4: git config --get core.commentchar
            u"different-brånch\n"        # context4: git rev-parse --abbrev-ref HEAD
        ])
        self.assertNotEqual(context1, context4)
