# -*- coding: utf-8 -*-

from sh import git, gitlint  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class CommitsTests(BaseTestCase):
    """ Integration tests for the --commits argument, i.e. linting multiple commits at once or linting specific commits
    """

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

    def test_lint_single_commit(self):
        self._create_simple_commit(u"Sïmple title.\n")
        self._create_simple_commit(u"Sïmple title2.\n")
        commit_sha = self.get_last_commit_hash()
        refspec = "{0}^...{0}".format(commit_sha)
        self._create_simple_commit(u"Sïmple title3.\n")
        output = gitlint("--commits", refspec, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        expected = (u"1: T3 Title has trailing punctuation (.): \"Sïmple title2.\"\n" +
                    u"3: B6 Body message is missing\n")
        self.assertEqual(output.exit_code, 2)
        self.assertEqual(output, expected)

    def test_lint_head(self):
        """ Testing whether we can also recognize special refs like 'HEAD' """
        tmp_git_repo = self.create_tmp_git_repo()
        self._create_simple_commit(u"Sïmple title.\n\nSimple bödy describing the commit", git_repo=tmp_git_repo)
        self._create_simple_commit(u"Sïmple title", git_repo=tmp_git_repo)
        self._create_simple_commit(u"WIP: Sïmple title\n\nSimple bödy describing the commit", git_repo=tmp_git_repo)
        output = gitlint("--commits", "HEAD", _cwd=tmp_git_repo, _tty_in=True, _ok_code=[3])
        revlist = git("rev-list", "HEAD", _tty_in=True, _cwd=tmp_git_repo).split()

        expected = (
            u"Commit {0}:\n".format(revlist[0][:10]) +
            u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Sïmple title\"\n\n" +
            u"Commit {0}:\n".format(revlist[1][:10]) +
            u"3: B6 Body message is missing\n\n" +
            u"Commit {0}:\n".format(revlist[2][:10]) +
            u"1: T3 Title has trailing punctuation (.): \"Sïmple title.\"\n"
        )

        self.assertEqual(output, expected)

    def test_ignore_commits(self):
        """ Tests multiple commits of which some rules get igonored because of ignore-* rules """
        # Create repo and some commits
        tmp_git_repo = self.create_tmp_git_repo()
        self._create_simple_commit(u"Sïmple title.\n\nSimple bödy describing the commit", git_repo=tmp_git_repo)
        # Normally, this commit will give T3 (trailing-punctuation), T5 (WIP) and B5 (bod-too-short) violations
        # But in this case only B5 because T3 and T5 are being ignored because of config
        self._create_simple_commit(u"Release: WIP tïtle.\n\nShort", git_repo=tmp_git_repo)
        # In the following 2 commits, the T3 violations are as normal
        self._create_simple_commit(
            u"Sïmple WIP title3.\n\nThis is \ta relëase commit\nMore info", git_repo=tmp_git_repo)
        self._create_simple_commit(u"Sïmple title4.\n\nSimple bödy describing the commit4", git_repo=tmp_git_repo)
        revlist = git("rev-list", "HEAD", _tty_in=True, _cwd=tmp_git_repo).split()

        config_path = self.get_sample_path("config/ignore-release-commits")
        output = gitlint("--commits", "HEAD", "--config", config_path, _cwd=tmp_git_repo, _tty_in=True, _ok_code=[4])

        expected = (
            u"Commit {0}:\n".format(revlist[0][:10]) +
            u"1: T3 Title has trailing punctuation (.): \"Sïmple title4.\"\n\n" +
            u"Commit {0}:\n".format(revlist[1][:10]) +
            u"1: T5 Title contains the word 'WIP' (case-insensitive): \"Sïmple WIP title3.\"\n\n" +
            u"Commit {0}:\n".format(revlist[2][:10]) +
            u"3: B5 Body message is too short (5<20): \"Short\"\n\n" +
            u"Commit {0}:\n".format(revlist[3][:10]) +
            u"1: T3 Title has trailing punctuation (.): \"Sïmple title.\"\n"
        )

        self.assertEqual(output, expected)
