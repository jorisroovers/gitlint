# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg

import re

from qa.shell import gitlint
from qa.base import BaseTestCase
from qa.utils import sstr, ustr


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
        # Test both on existing and new repo (we've had a bug in the past that was unique to empty repos)
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

    def test_config_from_env(self):
        """ Test for configuring gitlint from environment variables """

        # We invoke gitlint, configuring it via env variables, we can check whether gitlint picks these up correctly
        # by comparing the debug output with what we'd expect
        target_repo = self.create_tmp_git_repo()
        commit_msg = u"WIP: Thïs is a title thåt is a bit longer.\nContent on the second line\n" + \
                     "This line of the body is here because we need it"
        filename = self.create_simple_commit(commit_msg, git_repo=target_repo)
        env = self.create_environment({"GITLINT_DEBUG": "1", "GITLINT_VERBOSITY": "2",
                                       "GITLINT_IGNORE": "T1,T2", "GITLINT_CONTRIB": "CC1,CT1",
                                       "GITLINT_IGNORE_STDIN": "1", "GITLINT_TARGET": target_repo,
                                       "GITLINT_COMMITS": self.get_last_commit_hash(git_repo=target_repo)})
        output = gitlint(_env=env, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        expected_kwargs = self.get_debug_vars_last_commit(git_repo=target_repo)
        expected_kwargs.update({'changed_files': sstr([filename])})

        self.assertEqualStdout(output, self.get_expected("test_config/test_config_from_env_1", expected_kwargs))

        # For some env variables, we need a separate test ast they are mutually exclusive with the ones tested above
        tmp_commit_msg_file = self.create_tmpfile(u"WIP: msg-fïlename test.")
        env = self.create_environment({"GITLINT_DEBUG": "1", "GITLINT_TARGET": target_repo,
                                       "GITLINT_SILENT": "1", "GITLINT_STAGED": "1"})

        output = gitlint("--msg-filename", tmp_commit_msg_file,
                         _env=env, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])

        # Extract date from actual output to insert it into the expected output
        # We have to do this since there's no way for us to deterministically know that date otherwise
        p = re.compile("Date: (.*)\n", re.UNICODE | re.MULTILINE)
        result = p.search(ustr(output.stdout))
        date = result.group(1).strip()
        expected_kwargs.update({"date": date})

        self.assertEqualStdout(output, self.get_expected("test_config/test_config_from_env_2", expected_kwargs))
