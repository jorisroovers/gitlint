# -*- coding: utf-8 -*-

from sh import gitlint  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase


class UserDefinedRuleTests(BaseTestCase):
    """ Integration tests for user-defined rules."""

    def test_user_defined_rules(self):
        extra_path = self.get_example_path()
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self._create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[4])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Thi$ is å title\"\n" + \
                   "1: UC2 Body does not contain a 'Signed-Off-By' line\n" + \
                   u"1: UL1 Title contains the special character '$': \"WIP: Thi$ is å title\"\n" + \
                   "2: B4 Second line is not empty: \"Content on the second line\"\n"
        self.assertEqual(output, expected)

    def test_user_defined_rules_with_config(self):
        extra_path = self.get_example_path()
        commit_msg = u"WIP: Thi$ is å title\nContent on the second line"
        self._create_simple_commit(commit_msg)
        output = gitlint("--extra-path", extra_path, "-c", "body-max-line-count.max-line-count=1",
                         _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[5])
        expected = u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Thi$ is å title\"\n" + \
                   "1: UC1 Body contains too many lines (2 > 1)\n" + \
                   "1: UC2 Body does not contain a 'Signed-Off-By' line\n" + \
                   u"1: UL1 Title contains the special character '$': \"WIP: Thi$ is å title\"\n" + \
                   "2: B4 Second line is not empty: \"Content on the second line\"\n"

        self.assertEqual(output, expected)

    def test_invalid_user_defined_rules(self):
        extra_path = self.get_sample_path("user_rules/incorrect_linerule")
        self._create_simple_commit("WIP: test")
        output = gitlint("--extra-path", extra_path, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[255])
        self.assertEqual(output,
                         "Config Error: User-defined rule class 'MyUserLineRule' must have a 'validate' method\n")
