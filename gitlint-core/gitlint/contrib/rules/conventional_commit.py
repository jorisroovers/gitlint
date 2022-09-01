import re

from gitlint.options import ListOption
from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation

RULE_REGEX = re.compile(r"([^(]+?)(\([^)]+?\))?!?: .+")


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
        )
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

        return violations
