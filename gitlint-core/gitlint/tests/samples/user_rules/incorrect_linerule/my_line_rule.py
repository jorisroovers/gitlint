from gitlint.rules import LineRule


class MyUserLineRule(LineRule):
    id = "UC2"
    name = "my-lïne-rule"

    # missing validate method, missing target attribute
