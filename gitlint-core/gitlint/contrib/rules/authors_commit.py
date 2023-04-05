import re
from pathlib import Path
from typing import Set, Tuple

from gitlint.git import GitContext
from gitlint.rules import CommitRule, RuleViolation


class AllowedAuthors(CommitRule):
    """Enforce that only authors listed in the AUTHORS file are allowed to commit."""

    authors_file_names = ("AUTHORS", "AUTHORS.txt", "AUTHORS.md")
    parse_authors = re.compile(r"^(?P<name>.*) <(?P<email>.*)>$", re.MULTILINE)

    name = "contrib-allowed-authors"

    id = "CC3"

    @classmethod
    def _read_authors_from_file(cls, git_ctx: GitContext) -> Tuple[Set[str], str]:
        for file_name in cls.authors_file_names:
            if git_ctx.repository_path:
                path = Path(git_ctx.repository_path) / file_name
            else:
                path = Path(file_name)
            if path.exists():
                authors_file = path
                break
        else:
            raise FileNotFoundError("No AUTHORS file found!")

        authors_file_content = authors_file.read_text("utf-8")
        authors = re.findall(cls.parse_authors, authors_file_content)

        return set(authors), authors_file.name

    def validate(self, commit):
        registered_authors, authors_file_name = AllowedAuthors._read_authors_from_file(commit.message.context)

        author = (commit.author_name, commit.author_email.lower())

        if author not in registered_authors:
            return [
                RuleViolation(
                    self.id,
                    f"Author not in '{authors_file_name}' file: " f'"{commit.author_name} <{commit.author_email}>"',
                )
            ]
        return []
