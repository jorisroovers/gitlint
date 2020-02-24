# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
from qa.shell import gitlint
from qa.base import BaseTestCase
from qa.utils import sstr


class ConfigTests(BaseTestCase):
    """ Integration tests for gitlint configuration and configuration precedence. """

    def test_ignore_by_id(self):
        self.create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("--ignore", "T5,B4", _tty_in=True, _cwd=self.tmp_git_repo, _ok_code=[1])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n"
        self.assertEqualStdout(output, expected)

    def test_ignore_by_name(self):
        self.create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
        output = gitlint("--ignore", "title-must-not-contain-word,body-first-line-empty",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[1])
        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Thïs is a title.\"\n"
        self.assertEqualStdout(output, expected)

    def test_verbosity(self):
        self.create_simple_commit(u"WIP: Thïs is a title.\nContënt on the second line")
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
        self.create_simple_commit(u"This ïs a title.")
        output = gitlint("-c", "title-max-length.line-length=5", _tty_in=True, _cwd=self.tmp_git_repo, _ok_code=[3])
        self.assertEqualStdout(output, self.get_expected("test_config/test_set_rule_option_1"))

    def test_config_from_file(self):
        commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        self.create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/gitlintconfig")
        output = gitlint("--config", config_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        self.assertEqualStdout(output, self.get_expected("test_config/test_config_from_file_1"))

    def test_config_from_file_debug(self):
        # Test bot on existing and new repo (we've had a bug in the past that was unique to empty repos)
        repos = [self.tmp_git_repo, self.create_tmp_git_repo()]
        for target_repo in repos:
            commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                        "This line of the body is here because we need it"
            filename = self.create_simple_commit(commit_msg, git_repo=target_repo)
            config_path = self.get_sample_path("config/gitlintconfig")
            output = gitlint("--config", config_path, "--debug", _cwd=target_repo, _tty_in=True, _ok_code=[5])

            expected_kwargs = self.get_debug_vars_last_commit(git_repo=target_repo)
            expected_kwargs.update({'config_path': config_path, 'changed_files': sstr([filename])})
            self.assertEqualStdout(output, self.get_expected("test_config/test_config_from_file_debug_1",
                                                             expected_kwargs))
