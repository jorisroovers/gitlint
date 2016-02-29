from unittest import TestCase
from datetime import datetime
from uuid import uuid4
from sh import git, rm, gitlint, touch, echo, ErrorReturnCode


class BaseTestCase(TestCase):
    # In case of assert failures, print the full error message
    maxDiff = None


class IntegrationTests(BaseTestCase):
    """ Simple set of integration tests for gitlint """
    tmp_git_repo = None

    @classmethod
    def setUpClass(cls):
        """ Sets up the integration tests by creating a new temporary git repository """
        cls.tmp_git_repo = "/tmp/gitlint-test-%s" % datetime.now().strftime("%Y%m%d-%H%M%S")
        git("init", cls.tmp_git_repo)
        # configuring name and email is required in every git repot
        git("config", "user.name", "gitlint-test-user", _cwd=cls.tmp_git_repo)
        git("config", "user.email", "gitlint@test.com", _cwd=cls.tmp_git_repo)

    @classmethod
    def tearDownClass(cls):
        """ Cleans up the temporary git repository """
        rm("-rf", cls.tmp_git_repo)

    def _create_simple_commit(self, message, out=None):
        """ Creates a simple commit with an empty test file.
            :param message: Commit message for the commit. """
        test_filename = "test-file-" + str(uuid4())
        touch(test_filename, _cwd=self.tmp_git_repo)
        git("add", test_filename, _cwd=self.tmp_git_repo)
        # https://amoffat.github.io/sh/#interactive-callbacks
        git("commit", "-m", message, _cwd=self.tmp_git_repo, _tty_in=True, _out=out)
        return test_filename

    def test_successful(self):
        self._create_simple_commit("Simple title\n\nSimple body")
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqual(output, "")

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
