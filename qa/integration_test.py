from unittest import TestCase
from datetime import datetime
from uuid import uuid4
from sh import git, rm, gitlint, touch, echo, ErrorReturnCode


class BaseTestCase(TestCase):
    pass


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

    def _create_simple_commit(self, message):
        """ Creates a simple commit with an empty test file.
            :param message: Commit message for the commit. """
        test_filename = "test-file-" + str(uuid4())
        touch(test_filename, _cwd=self.tmp_git_repo)
        git("add", test_filename, _cwd=self.tmp_git_repo)
        git("commit", "-m", message, _cwd=self.tmp_git_repo)

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
