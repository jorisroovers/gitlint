from qa.base import BaseTestCase
from qa.shell import gitlint


class RuleTests(BaseTestCase):
    """
    Tests for specific rules that are worth testing as integration tests.
    It's not a goal to test every edge case of each rule, that's what the unit tests do.
    """

    def test_match_regex_rules(self):
        """
        Test that T7 (title-match-regex) and B8 (body-match-regex) work as expected.
        By default, these rules don't do anything, only when setting a custom regex will they run.
        """

        commit_msg = "Thåt dûr bår\n\nSïmple commit message body"
        self.create_simple_commit(commit_msg)

        # Assert violations when T7 and B8 regexes don't match
        output = gitlint("-c", "T7.regex=foo", "-c", "B8.regex=bar", _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        self.assertEqualStdout(output, self.get_expected("test_rules/test_match_regex_rules_1"))

        # Assert no violations when T7 and B8 regexes do match
        output = gitlint("-c", "T7.regex=^Thåt", "-c", "B8.regex=commit message", _cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqualStdout(output, "")

    def test_ignore_rules(self):
        """
        Test that ignore rules work as expected:
            ignore-by-title, ignore-by-body, ignore-by-author-name, ignore-body-lines
        By default, these rules don't do anything, only when setting a custom regex will they run.
        """
        commit_msg = "WIP: Commït Tïtle\n\nSïmple commit\tbody\nAnōther Line  \nLåst Line"
        self.create_simple_commit(commit_msg)

        # Assert violations when not ignoring anything
        output = gitlint(_cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[3])
        self.assertEqualStdout(output, self.get_expected("test_rules/test_ignore_rules_1"))

        # Simple convenience function that passes in common arguments for this test
        def invoke_gitlint(*args, **kwargs):
            return gitlint(
                *args, "-c", "general.regex-style-search=True", **kwargs, _cwd=self.tmp_git_repo, _tty_in=True
            )

        # ignore-by-title
        output = invoke_gitlint("-c", "ignore-by-title.regex=Commït")
        self.assertEqualStdout(output, "")

        # ignore-by-body
        output = invoke_gitlint("-c", "ignore-by-body.regex=Anōther Line")
        self.assertEqualStdout(output, "")

        # ignore-by-author-name
        output = invoke_gitlint("-c", "ignore-by-author-name.regex=gitlint-test-user")
        self.assertEqualStdout(output, "")

        # ignore-body-lines
        output = invoke_gitlint("-c", "ignore-body-lines.regex=^Anōther", _ok_code=[2])
        self.assertEqualStdout(output, self.get_expected("test_rules/test_ignore_rules_2"))
