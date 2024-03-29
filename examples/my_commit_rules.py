from gitlint.options import IntOption, ListOption
from gitlint.rules import CommitRule, RuleViolation

"""
Full details on user-defined rules: https://jorisroovers.github.io/gitlint/rules/user_defined_rules

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

    # A rule MUST have a *unique* id
    # we recommend starting with UC (for User-defined Commit-rule).
    id = "UC1"

    # A rule MAY have an option_spec if its behavior is configurable.
    options_spec = [
        IntOption(
            "max-line-count",  # option name
            3,  # default value
            "Maximum body line count",  # description
        )
    ]

    def validate(self, commit):
        line_count = len(commit.message.body)
        max_count = self.options["max-line-count"].value
        if line_count > max_count:
            msg = f"Body has too many lines ({line_count} > {max_count})"
            return [RuleViolation(self.id, msg, line_nr=1)]


class SignedOffBy(CommitRule):
    """Enforce that each commit contains a "Signed-off-by" line.
    We keep things simple here and just check whether the commit body
    contains a line that starts with "Signed-off-by".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id
    # We recommend starting with UC (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        log_msg = "This will be visible when running `gitlint --debug`"
        self.log.debug(log_msg)

        for line in commit.message.body:
            if line.startswith("Signed-off-by"):
                return

        msg = "Body does not contain a 'Signed-off-by' line"
        return [RuleViolation(self.id, msg, line_nr=1)]


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
