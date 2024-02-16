import re

from gitlint.options import ListOption
from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation

RULE_REGEX = re.compile(r"([^(]+?)(?:\(([^)]+?)\))?!?: .+")


class ConventionalCommit(LineRule):
    """This rule enforces the spec at https://www.conventionalcommits.org/."""

    name = "contrib-title-conventional-commits"
    id = "CT1"
    target = CommitMessageTitle

    options_spec = [
        ListOption(
            "types",
            ["fix", "feat", "chore", "docs", "style", "refactor", "perf", "test", "revert", "ci", "build"],
            "Comma separated list of allowed commit types.",
        ),
        ListOption(
            "scopes",
            [],
            "Comma separated list of allowed scopes.",
        ),
    ]

    def validate(self, line, _commit):
        violations = []
        match = RULE_REGEX.match(line)

        if not match:
            msg = "Title does not follow ConventionalCommits.org format 'type(optional-scope): description'"
            violations.append(RuleViolation(self.id, msg, line))
            return violations

        line_commit_type = match.group(1)
        if line_commit_type not in self.options["types"].value:
            opt_str = ", ".join(self.options["types"].value)
            violations.append(RuleViolation(self.id, f"Title does not start with one of {opt_str}", line))

        valid_scopes = self.options["scopes"].value
        if not valid_scopes:
            return violations

        line_commit_scope = match.group(2)
        if line_commit_scope and line_commit_scope not in valid_scopes:
            opt_str = ", ".join(valid_scopes)
            violations.append(RuleViolation(self.id, f"Title does not use one of these scopes: {opt_str}", line))

        return violations
