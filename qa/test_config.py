# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
import platform
import sys

import arrow

from qa.shell import git, gitlint
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
        self.assertEqualStdout(output, self.get_expected("test_config/test_verbosity_1"))

        output = gitlint("-vvv", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqualStdout(output, self.get_expected("test_config/test_verbosity_2"))

        # test silent mode
        output = gitlint("--silent", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqualStdout(output, "")

    def test_set_rule_option(self):
        self._create_simple_commit(u"This ïs a title.")
        output = gitlint("-c", "title-max-length.line-length=5", _tty_in=True, _cwd=self.tmp_git_repo, _ok_code=[3])
        self.assertEqualStdout(output, self.get_expected("test_config/test_set_rule_option_1"))

    def test_config_from_file(self):
        commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self._create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        self.assertEqualStdout(output, self.get_expected("test_config/test_config_from_file_1"))

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

        expected_kwargs = {'platform': platform.platform(), 'python_version': sys.version,
                           'git_version': expected_git_version, 'gitlint_version': expected_gitlint_version,
                           'GITLINT_USE_SH_LIB': self.GITLINT_USE_SH_LIB, 'config_path': config_path,
                           'target': self.tmp_git_repo, 'commit_sha': commit_sha, 'commit_date': expected_date}
        self.assertEqualStdout(output, self.get_expected("test_config/test_config_from_file_debug_1", expected_kwargs))
