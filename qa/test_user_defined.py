# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
from qa.shell import gitlint
from qa.base import BaseTestCase


class UserDefinedRuleTests(BaseTestCase):
    """ Integration tests for user-defined rules."""

    def test_user_defined_rules(self):
        extra_path = self.get_example_path()
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self._create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])
        self.assertEqualStdout(output, self.get_expected("test_user_defined/test_user_defined_rules_1"))

    def test_user_defined_rules_with_config(self):
        extra_path = self.get_example_path()
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self._create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, "-c", "body-max-line-count.max-line-count=1",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        self.assertEqualStdout(output, self.get_expected("test_user_defined/test_user_defined_rules_with_config_1"))

    def test_invalid_user_defined_rules(self):
        extra_path = self.get_sample_path("user_rules/incorrect_linerule")
        self._create_simple_commit("WIP: test")
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[255])
        self.assertEqualStdout(output,
                               "Config Error: User-defined rule class 'MyUserLineRule' must have a 'validate' method\n")
