# -*- coding: utf-8 -*-

from sh import git, gitlint  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class CommitsTests(BaseTestCase):
    """ Integration tests for linting multiple commits at once """

    def test_successful(self):
        """ Test linting multiple commits without violations """
        git("checkout", "-b", "test-branch-commits-base", _cwd=self.tmp_git_repo)
        self._create_simple_commit(u"Sïmple title\n\nSimple bödy describing the commit")
        git("checkout", "-b", "test-branch-commits", _cwd=self.tmp_git_repo)
        self._create_simple_commit(u"Sïmple title2\n\nSimple bödy describing the commit2")
        self._create_simple_commit(u"Sïmple title3\n\nSimple bödy describing the commit3")
        output = gitlint("--commits", "test-branch-commits-base...test-branch-commits",
                         _cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqual(output, "")

    def test_violations(self):
        """ Test linting multiple commits with violations """
        git("checkout", "-b", "test-branch-commits-violations-base", _cwd=self.tmp_git_repo)
        self._create_simple_commit(u"Sïmple title.\n")
        git("checkout", "-b", "test-branch-commits-violations", _cwd=self.tmp_git_repo)

        self._create_simple_commit(u"Sïmple title2.\n")
        commit_sha1 = self.get_last_commit_hash()[:10]
        self._create_simple_commit(u"Sïmple title3.\n")
        commit_sha2 = self.get_last_commit_hash()[:10]
        output = gitlint("--commits", "test-branch-commits-violations-base...test-branch-commits-violations",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])
        expected = (u"Commit {0}:\n".format(commit_sha2) +
                    u"1: T3 Title has trailing punctuation (.): \"Sïmple title3.\"\n" +
                    u"3: B6 Body message is missing\n"
                    "\n"
                    u"Commit {0}:\n".format(commit_sha1) +
                    u"1: T3 Title has trailing punctuation (.): \"Sïmple title2.\"\n"
                    u"3: B6 Body message is missing\n")

        self.assertEqual(output.exit_code, 4)
        self.assertEqual(output, expected)

    def test_single_commit(self):
        self._create_simple_commit(u"Sïmple title.\n")
        self._create_simple_commit(u"Sïmple title2.\n")
        commit_sha = self.get_last_commit_hash()
        self._create_simple_commit(u"Sïmple title3.\n")
        output = gitlint("--commits", commit_sha, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        expected = (u"1: T3 Title has trailing punctuation (.): \"Sïmple title2.\"\n" +
                    u"3: B6 Body message is missing\n")
        self.assertEqual(output.exit_code, 2)
        self.assertEqual(output, expected)
