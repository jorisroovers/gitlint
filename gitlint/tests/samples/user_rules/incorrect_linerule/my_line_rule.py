from gitlint.rules import LineRule


class MyUserLineRule(LineRule):
    id = "UC2"
    name = "my-line-rule"

    # missing validate method, missing target attribute
