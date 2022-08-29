from gitlint.rules import CommitRule, RuleViolation


class SignedOffBy(CommitRule):
    """This rule will enforce that each commit body contains a "Signed-off-by" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-off-by".
    """

    name = "contrib-body-requires-signed-off-by"
    id = "CC1"

    def validate(self, commit):
        for line in commit.message.body:
            if line.lower().startswith("signed-off-by"):
                return []

        return [RuleViolation(self.id, "Body does not contain a 'Signed-off-by' line", line_nr=1)]
