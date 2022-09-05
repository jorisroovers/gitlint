from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption


class MyUserCommitRule(CommitRule):
    name = "my-üser-commit-rule"
    id = "UC1"
    options_spec = [IntOption("violation-count", 1, "Number of violåtions to return")]

    def validate(self, _commit):
        violations = []
        for i in range(1, self.options["violation-count"].value + 1):
            violations.append(RuleViolation(self.id, "Commit violåtion %d" % i, "Contënt %d" % i, i))

        return violations


# The below code is present so that we can test that we actually ignore it


def func_should_be_ignored():
    pass


global_variable_should_be_ignored = True
