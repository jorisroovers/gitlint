# -*- coding: utf-8 -*-
# pylint: disable=too-many-function-args,unexpected-keyword-arg
from qa.shell import gitlint
from qa.base import BaseTestCase


class UserDefinedRuleTests(BaseTestCase):
    """ Integration tests for user-defined rules."""

    def test_user_defined_rules_examples1(self):
        """ Test the user defined rules in the top-level `examples/` directory """
        extra_path = self.get_example_path()
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self.create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        self.assertEqualStdout(output, self.get_expected("test_user_defined/test_user_defined_rules_examples_1"))

    def test_user_defined_rules_examples2(self):
        """ Test the user defined rules in the top-level `examples/` directory """
        extra_path = self.get_example_path()
        commit_msg = u"Release: Thi$ is å title\nContent on the second line\n$This line is ignored \nThis isn't\t\n"
        self.create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])
        self.assertEqualStdout(output, self.get_expected("test_user_defined/test_user_defined_rules_examples_2"))

    def test_user_defined_rules_examples_with_config(self):
        """ Test the user defined rules in the top-level `examples/` directory """
        extra_path = self.get_example_path()
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self.create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, "-c", "body-max-line-count.max-line-count=1",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[6])
        expected_path = "test_user_defined/test_user_defined_rules_examples_with_config_1"
        self.assertEqualStdout(output, self.get_expected(expected_path))

    def test_user_defined_rules_extra(self):
        extra_path = self.get_sample_path("user_rules/extra")
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self.create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[9])
        self.assertEqualStdout(output, self.get_expected("test_user_defined/test_user_defined_rules_extra_1",
                                                         {'repo-path': self.tmp_git_repo}))

    def test_invalid_user_defined_rules(self):
        extra_path = self.get_sample_path("user_rules/incorrect_linerule")
        self.create_simple_commit("WIP: test")
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[255])
        self.assertEqualStdout(output,
                               "Config Error: User-defined rule class 'MyUserLineRule' must have a 'validate' method\n")
