from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption

"""
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
    name = "body-max-line-count"
    id = "UC1"
    options_spec = [IntOption('body-max-line-count', 3, "Maximum body line count")]

    def validate(self, commit):
        if len(commit.message.body) > self.options['body-max-line-count']:
            return [RuleViolation(self.id, "Body contains too many lines")]


class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit contains a "Signed-Off-By" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-Off-By".
    """
    name = "body-requires-signed-off-by"
    id = "UC2"

    def validate(self, commit):
        for line in commit.message.body:
            if line.startswith("Signed-Off-By"):
                return []

        return [RuleViolation(self.id, "Body does not contain a 'Signed-Off-By Line'")]
