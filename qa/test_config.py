# -*- coding: utf-8 -*-

from sh import gitlint  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class ConfigTests(BaseTestCase):
    """ Integration tests for gitlint configuration and configuration precedence. """

    def test_ignore_by_code(self):
        self._create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("--ignore", "T5,B4", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n"
        self.assertEqual(output, expected)

    def test_ignore_by_name(self):
        self._create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("--ignore", "title-must-not-contain-word,body-first-line-empty",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n"
        self.assertEqual(output, expected)

    def test_verbosity(self):
        self._create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("-v", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T3\n1: T5\n2: B4\n"
        self.assertEqual(output, expected)

        output = gitlint("-vv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T3 Title has trailing punctuation (.)\n" + \
                   u"1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                   u"2: B4 Second line is not empty\n"
        self.assertEqual(output, expected)

        output = gitlint("-vvv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n" + \
                   u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Thïs is a title.\"\n" + \
                   u"2: B4 Second line is not empty: \"Contënt on the second line\"\n"
        self.assertEqual(output, expected)

        # test silent mode
        output = gitlint("--silent", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqual(output, "")

    def test_set_rule_option(self):
        self._create_simple_commit(u"This ïs a title.")
        output = gitlint("-c", "title-max-length.line-length=5", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T1 Title exceeds max length (16>5): \"This ïs a title.\"\n" + \
                   u"1: T3 Title has trailing punctuation (.): \"This ïs a title.\"\n" + \
                   "3: B6 Body message is missing\n"
        self.assertEqual(output, expected)

    def test_config_from_file(self):
        commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self._create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])

        expected = "1: T1 Title exceeds max length (42>20)\n" + \
                   "1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                   u"1: T5 Title contains the word 'thåt' (case-insensitive)\n" + \
                   "2: B4 Second line is not empty\n" + \
                   "3: B1 Line exceeds max length (48>30)\n"

        self.assertEqual(output, expected)

    def test_config_from_file_debug(self):
        commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self._create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, "--debug", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])

        expected = self.get_expected('debug_output1', {'config_path': config_path, 'target': self.tmp_git_repo})

        self.assertEqual(output, expected)
