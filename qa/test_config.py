# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
import platform
import sys

import arrow

from sh import gitlint, git  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class ConfigTests(BaseTestCase):
    """ Integration tests for gitlint configuration and configuration precedence. """

    def test_ignore_by_id(self):
        self._create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("--ignore", "T5,B4", _tty_in=True, _cwd=self.tmp_git_repo, _ok_code=[1])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n"
        self.assertEqualStdout(output, expected)

    def test_ignore_by_name(self):
        self._create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("--ignore", "title-must-not-contain-word,body-first-line-empty",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n"
        self.assertEqualStdout(output, expected)

    def test_verbosity(self):
        self._create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("-v", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T3\n1: T5\n2: B4\n"
        self.assertEqualStdout(output, expected)

        output = gitlint("-vv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T3 Title has trailing punctuation (.)\n" + \
                   u"1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                   u"2: B4 Second line is not empty\n"
        self.assertEqualStdout(output, expected)

        output = gitlint("-vvv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n" + \
                   u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Thïs is a title.\"\n" + \
                   u"2: B4 Second line is not empty: \"Contënt on the second line\"\n"
        self.assertEqualStdout(output, expected)

        # test silent mode
        output = gitlint("--silent", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqualStdout(output, "")

    def test_set_rule_option(self):
        self._create_simple_commit(u"This ïs a title.")
        output = gitlint("-c", "title-max-length.line-length=5", _tty_in=True, _cwd=self.tmp_git_repo, _ok_code=[3])
        expected = u"1: T1 Title exceeds max length (16>5): \"This ïs a title.\"\n" + \
                   u"1: T3 Title has trailing punctuation (.): \"This ïs a title.\"\n" + \
                   "3: B6 Body message is missing\n"
        self.assertEqualStdout(output, expected)

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

        self.assertEqualStdout(output, expected)

    def test_config_from_file_debug(self):
        commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self._create_simple_commit(commit_msg)
        commit_sha = self.get_last_commit_hash()
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, "--debug", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])

        expected_date = git("log", "-1", "--pretty=%ai", _cwd=self.tmp_git_repo)
        expected_date = arrow.get(str(expected_date), "YYYY-MM-DD HH:mm:ss Z").datetime
        expected_gitlint_version = gitlint("--version").replace("gitlint, version ", "").replace("\n", "")
        expected_git_version = git("--version").replace("\n", "")

        expected = self.get_expected('debug_output1', {'platform': platform.platform(), 'python_version': sys.version,
                                                       'git_version': expected_git_version,
                                                       'gitlint_version': expected_gitlint_version,
                                                       'config_path': config_path, 'target': self.tmp_git_repo,
                                                       'commit_sha': commit_sha, 'commit_date': expected_date})

        self.assertEqualStdout(output, expected)
