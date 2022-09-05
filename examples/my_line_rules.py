from gitlint.rules import LineRule, RuleViolation, CommitMessageTitle
from gitlint.options import ListOption

"""
Full details on user-defined rules: https://jorisroovers.com/gitlint/user_defined_rules

The SpecialChars class below is an example of a user-defined LineRule. Line rules are gitlint rules that only act on a
single line at once. Once the rule is discovered, gitlint will automatically take care of applying this rule
against each line of the commit message title or body (whether it is applied to the title or body is determined by the
`target` attribute of the class).

A LineRule contrasts with a CommitRule (see examples/my_commit_rules.py) in that a commit rule is only applied once on
an entire commit. This allows commit rules to implement more complex checks that span multiple lines and/or checks
that should only be done once per gitlint run.

While every LineRule can be implemented as a CommitRule, it's usually easier and more concise to go with a LineRule if
that fits your needs.
"""


class SpecialChars(LineRule):
    """This rule will enforce that the commit message title does not contain any of the following characters:
    $^%@!*()"""

    # A rule MUST have a human friendly name
    name = "title-no-special-chars"

    # A rule MUST have a *unique* id, we recommend starting with UL (for User-defined Line-rule), but this can
    # really be anything.
    id = "UL1"

    # A line-rule MUST have a target (not required for CommitRules).
    target = CommitMessageTitle

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [
        ListOption(
            "special-chars",
            ["$", "^", "%", "@", "!", "*", "(", ")"],
            "Comma separated list of characters that should not occur in the title",
        )
    ]

    def validate(self, line, _commit):
        self.log.debug("SpecialChars: This will be visible when running `gitlint --debug`")

        violations = []
        # options can be accessed by looking them up by their name in self.options
        for char in self.options["special-chars"].value:
            if char in line:
                msg = f"Title contains the special character '{char}'"
                violation = RuleViolation(self.id, msg, line)
                violations.append(violation)

        return violations
