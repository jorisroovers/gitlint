from collections import namedtuple
from unittest.mock import Mock, patch

import pytest

from gitlint.contrib.rules.authors_commit import Authors


Author = namedtuple("Author", "name, email")
GitCtx = namedtuple("GitCtx", "repository_path")
MockFile = namedtuple("MockFile", "name")


@pytest.fixture(name="git_ctx")
def gen_git_ctx(tmpdir):
    authors_file = tmpdir / "AUTHORS"
    authors_file.write_text("John Doe <john.doe@mail.com>\nBob Smith <bob.smith@mail.com>", "utf-8")
    return GitCtx(tmpdir)


AUTHOR_1 = Author("John Doe", "john.doe@mail.com")
AUTHOR_2 = Author("Bob Smith", "bob.smith@mail.com")


@pytest.mark.parametrize("author", [AUTHOR_1, AUTHOR_2])
def test_authors_succeeds(author, git_ctx):
    assert not validate_authors_rule(author.name, author.email, git_ctx)


@pytest.mark.parametrize(
    "email",
    [
        AUTHOR_2.email.capitalize(),
        AUTHOR_2.email.lower(),
        AUTHOR_2.email.upper(),
    ],
)
def test_authors_email_is_case_insensitive(email, git_ctx):
    assert not validate_authors_rule(AUTHOR_2.name, email, git_ctx)


@pytest.mark.parametrize("name", [AUTHOR_2.name.lower(), AUTHOR_2.name.upper()])
def test_authors_name_is_case_sensitive(name, git_ctx):
    assert validate_authors_rule(name, AUTHOR_2.email, git_ctx)


@pytest.mark.parametrize("name", ["", "root"])
def test_authors_bad_name_fails(name, git_ctx):
    assert validate_authors_rule(name, AUTHOR_2.email, git_ctx)


@pytest.mark.parametrize("email", ["", "root@example.com"])
def test_authors_bad_email_fails(email, git_ctx):
    assert validate_authors_rule(AUTHOR_2.name, email, git_ctx)


def test_authors_invalid_combination_fails(git_ctx):
    assert validate_authors_rule(AUTHOR_1.name, AUTHOR_2.email, git_ctx)


def validate_authors_rule(name, email, git_ctx):
    commit = Mock()
    commit.author_name = name
    commit.author_email = email
    commit.message.context = git_ctx

    rule = Authors()
    return rule.validate(commit)


@patch(
    "gitlint.contrib.rules.authors_commit.Path.read_text",
    return_value="John Doe <john.doe@mail.com>",
)
def test_read_authors_file(_mock_read_text, git_ctx):
    authors, authors_file_name = Authors._read_authors_from_file(git_ctx)
    assert authors_file_name == "AUTHORS"
    assert len(authors) == 1
    assert authors == {AUTHOR_1}


@patch(
    "gitlint.contrib.rules.authors_commit.Path.exists",
    return_value=False,
)
def test_read_authors_file_missing_file(_mock_iterdir, git_ctx):
    with pytest.raises(FileNotFoundError):
        Authors._read_authors_from_file(git_ctx)
