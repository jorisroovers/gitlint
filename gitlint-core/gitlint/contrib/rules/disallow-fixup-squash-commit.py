from gitlint.rules import CommitRule, RuleViolation

class DisallowCleanupCommits(CommitRule):
    name = "contrib-disallow-cleanup-commits"
    id = "CC2"

    def validate(self, commit):
        if commit.is_fixup_commit:
            return [RuleViolation(self.id, "Fixup commits are not allowed", line_nr=1)]

        if commit.is_squash_commit:
            return [RuleViolation(self.id, "Squash commits are not allowed", line_nr=1)]

