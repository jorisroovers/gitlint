from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption


class MyUserCommitRule(CommitRule):
    name = "my-user-commit-rule"
    id = "TUC1"
    options_spec = [IntOption('violation-count', 0, "Number of violations to return")]

    def validate(self, _commit):
        violations = []
        for i in range(1, self.options['violation-count'].value + 1):
            violations.append(RuleViolation(self.id, "Commit violation %d" % i, "Content %d" % i, i))

        return violations
