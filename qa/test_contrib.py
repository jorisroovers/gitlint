# -*- coding: utf-8 -*-
# pylint: disable=
from qa.shell import gitlint
from qa.base import BaseTestCase


class ContribRuleTests(BaseTestCase):
    """ Integration tests for contrib rules."""

    def test_contrib_rules(self):
        self.create_simple_commit(u"WIP Thi$ is å title\n\nMy bödy that is a bit longer than 20 chars")
        output = gitlint("--contrib", "contrib-title-conventional-commits,CC1",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])
        self.assertEqualStdout(output, self.get_expected("test_contrib/test_contrib_rules_1"))

    def test_contrib_rules_with_config(self):
        self.create_simple_commit(u"WIP Thi$ is å title\n\nMy bödy that is a bit longer than 20 chars")
        output = gitlint("--contrib", "contrib-title-conventional-commits,CC1",
                         "-c", u"contrib-title-conventional-commits.types=föo,bår",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])
        self.assertEqualStdout(output, self.get_expected("test_contrib/test_contrib_rules_with_config_1"))

    def test_invalid_contrib_rules(self):
        self.create_simple_commit("WIP: test")
        output = gitlint("--contrib", u"föobar,CC1", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[255])
        self.assertEqualStdout(output, u"Config Error: No contrib rule with id or name 'föobar' found.\n")
