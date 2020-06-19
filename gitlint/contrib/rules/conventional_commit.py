import re

from gitlint.options import ListOption
from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation
from gitlint.utils import ustr

RULE_REGEX = re.compile(r"[^(]+?(\([^)]+?\))?: .+")


class ConventionalCommit(LineRule):
    """ This rule enforces the spec at https://www.conventionalcommits.org/. """

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

        for commit_type in self.options["types"].value:
            if line.startswith(ustr(commit_type)):
                break
        else:
            msg = u"Title does not start with one of {0}".format(', '.join(self.options['types'].value))
            violations.append(RuleViolation(self.id, msg, line))

        if not RULE_REGEX.match(line):
            msg = u"Title does not follow ConventionalCommits.org format 'type(optional-scope): description'"
            violations.append(RuleViolation(self.id, msg, line))

        return violations
