# -*- coding: utf-8 -*-
from qa.shell import gitlint
from qa.base import BaseTestCase


class NamedRuleTests(BaseTestCase):
    """ Integration tests for named rules."""

    def test_named_rule(self):
        commit_msg = u"WIP: thåt dûr bår\n\nSïmple commit body"
        self.create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/named-rules")
        output = gitlint("--config", config_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        self.assertEqualStdout(output, self.get_expected("test_named_rules/test_named_rule_1"))

    def test_named_user_rule(self):
        commit_msg = u"Normal cömmit title\n\nSïmple commit message body"
        self.create_simple_commit(commit_msg)
        config_path = self.get_sample_path("config/named-user-rules")
        extra_path = self.get_sample_path("user_rules/extra")
        output = gitlint("--extra-path", extra_path, "--config", config_path, _cwd=self.tmp_git_repo, _tty_in=True,
                         _ok_code=[9])
        self.assertEqualStdout(output, self.get_expected("test_named_rules/test_named_user_rule_1"))
