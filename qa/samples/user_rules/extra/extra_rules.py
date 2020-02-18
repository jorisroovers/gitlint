from gitlint.rules import CommitRule, RuleViolation
from gitlint.utils import sstr


class GitContextRule(CommitRule):
    """ Rule that tests whether we can correctly access certain gitcontext properties """
    name = "gitcontext"
    id = "UC1"

    def validate(self, commit):
        violations = [
            RuleViolation(self.id, "GitContext.current_branch: {0}".format(commit.context.current_branch), line_nr=1),
            RuleViolation(self.id, "GitContext.commentchar: {0}".format(commit.context.commentchar), line_nr=1)
        ]

        return violations


class GitCommitRule(CommitRule):
    """ Rule that tests whether we can correctly access certain commit properties """
    name = "gitcommit"
    id = "UC2"

    def validate(self, commit):
        violations = [
            RuleViolation(self.id, "GitCommit.branches: {0}".format(sstr(commit.branches)), line_nr=1),
        ]

        return violations
