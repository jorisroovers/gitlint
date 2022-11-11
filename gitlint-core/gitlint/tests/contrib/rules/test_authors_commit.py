from collections import namedtuple
from unittest.mock import patch
from gitlint.tests.base import BaseTestCase
from gitlint.rules import RuleViolation
from gitlint.config import LintConfig

from gitlint.contrib.rules.authors_commit import AllowedAuthors


class ContribAuthorsCommitTests(BaseTestCase):
    def setUp(self):
        author = namedtuple("Author", "name, email")
        self.author_1 = author("John Doe", "john.doe@mail.com")
        self.author_2 = author("Bob Smith", "bob.smith@mail.com")
        self.rule = AllowedAuthors()
        self.gitcontext = self.get_gitcontext()

    def get_gitcontext(self):
        gitcontext = self.gitcontext(self.get_sample("commit_message/sample1"))
        gitcontext.repository_path = self.get_sample_path("config")
        return gitcontext

    def get_commit(self, name, email):
        commit = self.gitcommit("commit_message/sample1", author_name=name, author_email=email)
        commit.message.context = self.gitcontext
        return commit

    def test_enable(self):
        for rule_ref in ["CC3", "contrib-allowed-authors"]:
            config = LintConfig()
            config.contrib = [rule_ref]
            self.assertIn(AllowedAuthors(), config.rules)

    def test_authors_succeeds(self):
        for author in [self.author_1, self.author_2]:
            commit = self.get_commit(author.name, author.email)
            violations = self.rule.validate(commit)
            self.assertListEqual([], violations)

    def test_authors_email_is_case_insensitive(self):
        for email in [
            self.author_2.email.capitalize(),
            self.author_2.email.lower(),
            self.author_2.email.upper(),
        ]:
            commit = self.get_commit(self.author_2.name, email)
            violations = self.rule.validate(commit)
            self.assertListEqual([], violations)

    def test_authors_name_is_case_sensitive(self):
        for name in [self.author_2.name.lower(), self.author_2.name.upper()]:
            commit = self.get_commit(name, self.author_2.email)
            violations = self.rule.validate(commit)
            expected_violation = RuleViolation(
                "CC3",
                f"Author not in 'AUTHORS' file: " f'"{name} <{self.author_2.email}>"',
            )
            self.assertListEqual([expected_violation], violations)

    def test_authors_bad_name_fails(self):
        for name in ["", "root"]:
            commit = self.get_commit(name, self.author_2.email)
            violations = self.rule.validate(commit)
            expected_violation = RuleViolation(
                "CC3",
                f"Author not in 'AUTHORS' file: " f'"{name} <{self.author_2.email}>"',
            )
            self.assertListEqual([expected_violation], violations)

    def test_authors_bad_email_fails(self):
        for email in ["", "root@example.com"]:
            commit = self.get_commit(self.author_2.name, email)
            violations = self.rule.validate(commit)
            expected_violation = RuleViolation(
                "CC3",
                f"Author not in 'AUTHORS' file: " f'"{self.author_2.name} <{email}>"',
            )
            self.assertListEqual([expected_violation], violations)

    def test_authors_invalid_combination_fails(self):
        commit = self.get_commit(self.author_1.name, self.author_2.email)
        violations = self.rule.validate(commit)
        expected_violation = RuleViolation(
            "CC3",
            f"Author not in 'AUTHORS' file: " f'"{self.author_1.name} <{self.author_2.email}>"',
        )
        self.assertListEqual([expected_violation], violations)

    @patch(
        "gitlint.contrib.rules.authors_commit.Path.read_text",
        return_value="John Doe <john.doe@mail.com>",
    )
    def test_read_authors_file(self, _mock_read_text):
        authors, authors_file_name = AllowedAuthors._read_authors_from_file(self.gitcontext)
        self.assertEqual(authors_file_name, "AUTHORS")
        self.assertEqual(len(authors), 1)
        self.assertEqual(authors, {self.author_1})

    @patch(
        "gitlint.contrib.rules.authors_commit.Path.exists",
        return_value=False,
    )
    def test_read_authors_file_missing_file(self, _mock_iterdir):
        with self.assertRaises(FileNotFoundError) as err:
            AllowedAuthors._read_authors_from_file(self.gitcontext)
            self.assertEqual(err.exception.args[0], "AUTHORS file not found")
