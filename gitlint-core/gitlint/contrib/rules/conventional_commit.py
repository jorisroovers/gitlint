import re

from gitlint.options import ListOption, BoolOption
from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation

RULE_REGEX = re.compile(r"([^(]+?)(\(([^)]+?)\))?!?: .+")


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
            "Comma separated list of allowed scopes. An empty list will allow anything.",
        ),
        BoolOption("require-scope", False, "Whether to require a scope."),
    ]

    def validate(self, line, _commit):
        violations = []
        match = RULE_REGEX.match(line)

        if not match:
            msg = "Title does not follow ConventionalCommits.org format 'type(optional-scope): description'"
            violations.append(RuleViolation(self.id, msg, line))
        else:
            line_commit_type = match.group(1)
            if line_commit_type not in self.options["types"].value:
                opt_str = ", ".join(self.options["types"].value)
                violations.append(RuleViolation(self.id, f"Title does not start with one of {opt_str}", line))

            line_scope = match.group(3)
            allowed_scopes = self.options["scopes"].value
            if line_scope and allowed_scopes and line_scope not in allowed_scopes:
                opt_str = ", ".join(self.options["scopes"].value)
                violations.append(RuleViolation(self.id, f"Scope is not one of {opt_str}", line))
            elif not line_scope and self.options["require-scope"].value:
                violations.append(RuleViolation(self.id, "Scope is required", line))

        return violations
