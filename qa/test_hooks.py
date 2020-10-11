# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
import os
from qa.shell import git, gitlint
from qa.base import BaseTestCase


class HookTests(BaseTestCase):
    """ Integration tests for gitlint commitmsg hooks"""

    VIOLATIONS = ['gitlint: checking commit message...\n',
                  u'1: T3 Title has trailing punctuation (.): "WIP: This ïs a title."\n',
                  u'1: T5 Title contains the word \'WIP\' (case-insensitive): "WIP: This ïs a title."\n',
                  u'2: B4 Second line is not empty: "Contënt on the second line"\n',
                  '3: B6 Body message is missing\n',
                  '-----------------------------------------------\n',
                  'gitlint: \x1b[31mYour commit message contains the above violations.\x1b[0m\n']

    def setUp(self):
        self.responses = []
        self.response_index = 0
        self.githook_output = []

        # The '--staged' flag used in the commit-msg hook fetches additional information from the underlying
        # git repo which means there already needs to be a commit in the repo
        # (as gitlint --staged doesn't work against empty repos)
        self.create_simple_commit(u"Commït Title\n\nCommit Body explaining commit.")

        # install git commit-msg hook and assert output
        output_installed = gitlint("install-hook", _cwd=self.tmp_git_repo)
        expected_installed = u"Successfully installed gitlint commit-msg hook in %s/.git/hooks/commit-msg\n" % \
                             self.tmp_git_repo
        self.assertEqualStdout(output_installed, expected_installed)

    def tearDown(self):
        # uninstall git commit-msg hook and assert output
        output_uninstalled = gitlint("uninstall-hook", _cwd=self.tmp_git_repo)
        expected_uninstalled = u"Successfully uninstalled gitlint commit-msg hook from %s/.git/hooks/commit-msg\n" % \
                               self.tmp_git_repo
        self.assertEqualStdout(output_uninstalled, expected_uninstalled)

    def _violations(self):
        # Make a copy of the violations array so that we don't inadvertently edit it in the test (like I did :D)
        return list(self.VIOLATIONS)

        # callback function that captures git commit-msg hook output

    def _interact(self, line, stdin):
        self.githook_output.append(line)
        # Answer 'yes' to question to keep violating commit-msg
        if "Your commit message contains the above violations" in line:
            response = self.responses[self.response_index]
            stdin.put("{0}\n".format(response))
            self.response_index = (self.response_index + 1) % len(self.responses)

    def test_commit_hook_no_violations(self):
        test_filename = self.create_simple_commit(u"This ïs a title\n\nBody contënt that should work",
                                                  out=self._interact, tty_in=True)

        short_hash = self.get_last_commit_short_hash()
        expected_output = ["gitlint: checking commit message...\n",
                           "gitlint: \x1b[32mOK\x1b[0m (no violations in commit message)\n",
                           u"[master %s] This ïs a title\n" % short_hash,
                           " 1 file changed, 0 insertions(+), 0 deletions(-)\n",
                           u" create mode 100644 %s\n" % test_filename]
        self.assertListEqual(expected_output, self.githook_output)

    def test_commit_hook_continue(self):
        self.responses = ["y"]
        test_filename = self.create_simple_commit(u"WIP: This ïs a title.\nContënt on the second line",
                                                  out=self._interact, tty_in=True)

        # Determine short commit-msg hash, needed to determine expected output
        short_hash = self.get_last_commit_short_hash()

        expected_output = self._violations()
        expected_output += ["Continue with commit anyways (this keeps the current commit message)? " +
                            "[y(es)/n(no)/e(dit)] " +
                            u"[master %s] WIP: This ïs a title. Contënt on the second line\n"
                            % short_hash,
                            " 1 file changed, 0 insertions(+), 0 deletions(-)\n",
                            u" create mode 100644 %s\n" % test_filename]

        assert len(self.githook_output) == len(expected_output)
        for output, expected in zip(self.githook_output, expected_output):
            self.assertMultiLineEqual(
                output.replace('\r', ''),
                expected.replace('\r', ''))

    def test_commit_hook_abort(self):
        self.responses = ["n"]
        test_filename = self.create_simple_commit(u"WIP: This ïs a title.\nContënt on the second line",
                                                  out=self._interact, ok_code=1, tty_in=True)
        git("rm", "-f", test_filename, _cwd=self.tmp_git_repo)

        # Determine short commit-msg hash, needed to determine expected output

        expected_output = self._violations()
        expected_output += ["Continue with commit anyways (this keeps the current commit message)? " +
                            "[y(es)/n(no)/e(dit)] " +
                            "Commit aborted.\n",
                            "Your commit message: \n",
                            "-----------------------------------------------\n",
                            u"WIP: This ïs a title.\n",
                            u"Contënt on the second line\n",
                            "-----------------------------------------------\n"]

        self.assertListEqual(expected_output, self.githook_output)

    def test_commit_hook_edit(self):
        self.responses = ["e", "y"]
        env = {"EDITOR": ":"}
        test_filename = self.create_simple_commit(u"WIP: This ïs a title.\nContënt on the second line",
                                                  out=self._interact, env=env, tty_in=True)
        git("rm", "-f", test_filename, _cwd=self.tmp_git_repo)

        short_hash = git("rev-parse", "--short", "HEAD", _cwd=self.tmp_git_repo, _tty_in=True).replace("\n", "")

        # Determine short commit-msg hash, needed to determine expected output

        expected_output = self._violations()
        expected_output += ['Continue with commit anyways (this keeps the current commit message)? ' +
                            '[y(es)/n(no)/e(dit)] ' + self._violations()[0]]
        expected_output += self._violations()[1:]
        expected_output += ['Continue with commit anyways (this keeps the current commit message)? ' +
                            "[y(es)/n(no)/e(dit)] " +
                            u"[master %s] WIP: This ïs a title. Contënt on the second line\n" % short_hash,
                            " 1 file changed, 0 insertions(+), 0 deletions(-)\n",
                            u" create mode 100644 %s\n" % test_filename]

        assert len(self.githook_output) == len(expected_output)
        for output, expected in zip(self.githook_output, expected_output):
            self.assertMultiLineEqual(
                output.replace('\r', ''),
                expected.replace('\r', ''))

    def test_commit_hook_worktree(self):
        """ Tests that hook installation and un-installation also work in git worktrees.
        Test steps:
            ```sh
            git init <tmpdir>
            cd <tmpdir>
            git worktree add <worktree-tempdir>
            cd <worktree-tempdir>
            gitlint install-hook
            gitlint uninstall-hook
            ```
        """
        tmp_git_repo = self.create_tmp_git_repo()
        self.create_simple_commit(u"Simple title\n\nContënt in the body", git_repo=tmp_git_repo)

        worktree_dir = self.generate_temp_path()
        self.tmp_git_repos.append(worktree_dir)  # make sure we clean up the worktree afterwards

        git("worktree", "add", worktree_dir, _cwd=tmp_git_repo, _tty_in=True)

        output_installed = gitlint("install-hook", _cwd=worktree_dir)
        expected_hook_path = os.path.join(tmp_git_repo, ".git", "hooks", "commit-msg")
        expected_msg = "Successfully installed gitlint commit-msg hook in {0}\n".format(expected_hook_path)
        self.assertEqual(output_installed, expected_msg)

        output_uninstalled = gitlint("uninstall-hook", _cwd=worktree_dir)
        expected_hook_path = os.path.join(tmp_git_repo, ".git", "hooks", "commit-msg")
        expected_msg = "Successfully uninstalled gitlint commit-msg hook from {0}\n".format(expected_hook_path)
        self.assertEqual(output_uninstalled, expected_msg)
