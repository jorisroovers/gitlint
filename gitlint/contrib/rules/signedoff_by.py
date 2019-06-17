
from gitlint.rules import CommitRule, RuleViolation


class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit body contains a "Signed-Off-By" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-Off-By".
    """

    name = "contrib-body-requires-signed-off-by"
    id = "CC1"

    def validate(self, commit):
        for line in commit.message.body:
            if line.startswith("Signed-Off-By"):
                return []

        return [RuleViolation(self.id, "Body does not contain a 'Signed-Off-By' line", line_nr=1)]
