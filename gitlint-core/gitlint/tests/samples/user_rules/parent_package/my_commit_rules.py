from gitlint.rules import CommitRule


class MyUserCommitRule(CommitRule):
    name = "my-user-cömmit-rule"
    id = "UC2"
    options_spec = []

    def validate(self, _commit):
        return []
