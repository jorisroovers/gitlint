from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption, ListOption

"""
Full details on user-defined rules: https://jorisroovers.com/gitlint/user_defined_rules

The classes below are examples of user-defined CommitRules. Commit rules are gitlint rules that
act on the entire commit at once. Once the rules are discovered, gitlint will automatically take care of applying them
to the entire commit. This happens exactly once per commit.

A CommitRule contrasts with a LineRule (see examples/my_line_rules.py) in that a commit rule is only applied once on
an entire commit. This allows commit rules to implement more complex checks that span multiple lines and/or checks
that should only be done once per gitlint run.

While every LineRule can be implemented as a CommitRule, it's usually easier and more concise to go with a LineRule if
that fits your needs.
"""


class BodyMaxLineCount(CommitRule):
    # A rule MUST have a human friendly name
    name = "body-max-line-count"

    # A rule MUST have a *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC1"

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [IntOption("max-line-count", 3, "Maximum body line count")]

    def validate(self, commit):
        self.log.debug("BodyMaxLineCount: This will be visible when running `gitlint --debug`")

        line_count = len(commit.message.body)
        max_line_count = self.options["max-line-count"].value
        if line_count > max_line_count:
            message = f"Body contains too many lines ({line_count} > {max_line_count})"
            return [RuleViolation(self.id, message, line_nr=1)]


class SignedOffBy(CommitRule):
    """This rule will enforce that each commit contains a "Signed-off-by" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-off-by".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        self.log.debug("SignedOffBy: This will be visible when running `gitlint --debug`")

        for line in commit.message.body:
            if line.startswith("Signed-off-by"):
                return

        return [RuleViolation(self.id, "Body does not contain a 'Signed-off-by' line", line_nr=1)]


class BranchNamingConventions(CommitRule):
    """This rule will enforce that a commit is part of a branch that meets certain naming conventions.
    See GitFlow for real-world example of this: https://nvie.com/posts/a-successful-git-branching-model/
    """

    # A rule MUST have a human friendly name
    name = "branch-naming-conventions"

    # A rule MUST have a *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC3"

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [ListOption("branch-prefixes", ["feature/", "hotfix/", "release/"], "Allowed branch prefixes")]

    def validate(self, commit):
        self.log.debug("BranchNamingConventions: This line will be visible when running `gitlint --debug`")

        violations = []
        allowed_branch_prefixes = self.options["branch-prefixes"].value
        for branch in commit.branches:
            valid_branch_name = False

            for allowed_prefix in allowed_branch_prefixes:
                if branch.startswith(allowed_prefix):
                    valid_branch_name = True
                    break

            if not valid_branch_name:
                msg = f"Branch name '{branch}' does not start with one of {allowed_branch_prefixes}"
                violations.append(RuleViolation(self.id, msg, line_nr=1))

        return violations
