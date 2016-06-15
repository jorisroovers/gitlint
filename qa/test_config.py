from sh import gitlint  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class ConfigTests(BaseTestCase):
    def test_ignore_by_code(self):
        self._create_simple_commit("WIP: This is a title.\nContent on the second line")
        output = gitlint("--ignore", "T5,B4", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = "1: T3 Title has trailing punctuation (.): \"WIP: This is a title.\"\n"
        self.assertEqual(output, expected)

    def test_ignore_by_name(self):
        self._create_simple_commit("WIP: This is a title.\nContent on the second line")
        output = gitlint("--ignore", "title-must-not-contain-word,body-first-line-empty",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = "1: T3 Title has trailing punctuation (.): \"WIP: This is a title.\"\n"
        self.assertEqual(output, expected)

    def test_verbosity(self):
        self._create_simple_commit("WIP: This is a title.\nContent on the second line")
        output = gitlint("-v", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = "1: T3\n1: T5\n2: B4\n"
        self.assertEqual(output, expected)

        output = gitlint("-vv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = "1: T3 Title has trailing punctuation (.)\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                   "2: B4 Second line is not empty\n"
        self.assertEqual(output, expected)

        output = gitlint("-vvv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = "1: T3 Title has trailing punctuation (.): \"WIP: This is a title.\"\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: This is a title.\"\n" + \
                   "2: B4 Second line is not empty: \"Content on the second line\"\n"
        self.assertEqual(output, expected)

        # test silent mode
        output = gitlint("--silent", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqual(output, "")

    def test_set_rule_option(self):
        self._create_simple_commit("This is a title.")
        output = gitlint("-c", "title-max-length.line-length=5", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = "1: T1 Title exceeds max length (16>5): \"This is a title.\"\n" + \
                   "1: T3 Title has trailing punctuation (.): \"This is a title.\"\n" + \
                   "3: B6 Body message is missing\n"
        self.assertEqual(output, expected)

    def test_config_from_file(self):
        commit_msg = "WIP: This is a title that is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self._create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])

        expected = "1: T1 Title exceeds max length (42>20)\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                   "2: B4 Second line is not empty\n" + \
                   "3: B1 Line exceeds max length (48>30)\n"

        # TODO(jroovers): test for trailing whitespace -> git automatically strips whitespace when passing
        # taking a commit message via 'git commit -m'

        self.assertEqual(output, expected)

    def test_config_from_file_debug(self):
        commit_msg = "WIP: This is a title that is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self._create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, "--debug", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])

        expected = "Using config from %s\n" % config_path + \
                   "1: T1 Title exceeds max length (42>20)\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                   "2: B4 Second line is not empty\n" + \
                   "3: B1 Line exceeds max length (48>30)\n"

        # TODO(jroovers): test for trailing whitespace -> git automatically strips whitespace when passing
        # taking a commit message via 'git commit -m'

        self.assertEqual(output, expected)
