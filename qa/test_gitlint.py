from sh import git, gitlint, echo, ErrorReturnCode
from base import BaseTestCase


class IntegrationTests(BaseTestCase):
    """ Simple set of integration tests for gitlint """

    def test_successful(self):
        self._create_simple_commit("Simple title\n\nSimple body")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqual(output, "")

    def test_successful_merge_commit(self):
        # Create branch on master
        self._create_simple_commit("Commit on master\n\nSimple body")

        # Create test branch, add a commit and determine the commit hash
        git("checkout", "-b", "test-branch", _cwd=self.tmp_git_repo)
        git("checkout", "test-branch", _cwd=self.tmp_git_repo)
        commit_title = "Commit on test-branch with a pretty long title that will cause issues when merging"
        self._create_simple_commit("{0}\n\nSimple body".format(commit_title))
        hash = git("rev-parse", "HEAD", _cwd=self.tmp_git_repo, _tty_in=True).replace("\n", "")

        # Checkout master and merge the commit
        # We explicitly set the title of the merge commit to the title of the previous commit as this or similar
        # behavior is what many tools do that handle merges (like github, gerrit, etc).
        git("checkout", "master", _cwd=self.tmp_git_repo)
        git("merge", "--no-ff", "-m", "Merge '{0}'".format(commit_title), hash, _cwd=self.tmp_git_repo)

        # Run gitlint and assert output is empty
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqual(output, "")

        # Assert that we do see the error if we disable the ignore-merge-commits option
        output = gitlint("-c", "general.ignore-merge-commits=false", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        self.assertEqual(output, "1: T1 Title exceeds max length (90>72): \"Merge '{0}'\"\n".format(commit_title))

    def test_errors(self):
        commit_msg = "WIP: This is a title.\nContent on the second line"
        self._create_simple_commit(commit_msg)
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = "1: T3 Title has trailing punctuation (.): \"WIP: This is a title.\"\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: This is a title.\"\n" + \
                   "2: B4 Second line is not empty: \"Content on the second line\"\n"
        self.assertEqual(output, expected)

    def test_pipe_input(self):
        error_msg = None
        # For some odd reason, sh doesn't return the error output when piping something into gitlint.
        # Note that this does work as expected in the test_errors testcase.
        # To work around this we raise and catch an exception
        try:
            gitlint(echo("WIP: Pipe test."), _tty_in=False)
        except ErrorReturnCode as e:
            # StdErr is returned as bytes -> decode to unicode string
            # http://stackoverflow.com/questions/606191/convert-bytes-to-a-python-string
            error_msg = e.stderr.decode("utf-8")

        expected = "1: T3 Title has trailing punctuation (.): \"WIP: Pipe test.\"\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Pipe test.\"\n" + \
                   "3: B6 Body message is missing\n"

        self.assertEqual(error_msg, expected)

    def test_commit_hook(self):
        # install git commit-msg hook
        output_installed = gitlint("install-hook", _cwd=self.tmp_git_repo)
        expected_installed = "Successfully installed gitlint commit-msg hook in %s/.git/hooks/commit-msg\n" % \
                             self.tmp_git_repo

        githook_output = []

        # callback function that captures git commit-msg hook output
        def interact(line, stdin):
            githook_output.append(line)
            # Answer 'yes' to question to keep violating commit-msg
            if "Your commit message contains the above violations" in line:
                stdin.put("y\n")

        test_filename = self._create_simple_commit("WIP: This is a title.\nContent on the second line", out=interact)
        # Determine short commit-msg hash, needed to determine expected output
        short_hash = git("rev-parse", "--short", "HEAD", _cwd=self.tmp_git_repo, _tty_in=True).replace("\n", "")

        expected_output = ['gitlint: checking commit message...\n',
                           '1: T3 Title has trailing punctuation (.): "WIP: This is a title."\n',
                           '1: T5 Title contains the word \'WIP\' (case-insensitive): "WIP: This is a title."\n',
                           '2: B4 Second line is not empty: "Content on the second line"\n',
                           '3: B6 Body message is missing\n',
                           '-----------------------------------------------\n',
                           'gitlint: \x1b[31mYour commit message contains the above violations.\x1b[0m\n',
                           'Continue with commit anyways (this keeps the current commit message)? [y/n] ' +
                           '[master (root-commit) %s] WIP: This is a title. Content on the second line\n' % short_hash,
                           ' 1 file changed, 0 insertions(+), 0 deletions(-)\n',
                           ' create mode 100644 %s\n' % test_filename]

        # uninstall git commit-msg hook
        output_uninstalled = gitlint("uninstall-hook", _cwd=self.tmp_git_repo)
        expected_uninstalled = "Successfully uninstalled gitlint commit-msg hook from %s/.git/hooks/commit-msg\n" % \
                               self.tmp_git_repo

        # Do all assertaions at the end so that the uninstall happens even if we have an assertion that doesn't
        # work out. This doesn't block the other tests.
        self.assertEqual(output_installed, expected_installed)
        self.assertListEqual(expected_output, githook_output)
        self.assertEqual(output_uninstalled, expected_uninstalled)
