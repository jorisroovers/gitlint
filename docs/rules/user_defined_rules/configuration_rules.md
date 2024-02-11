[:octicons-tag-24: v0.14.0][v0.14.0] 

Configuration rules are special rules that are applied once per commit and **BEFORE** any other rules are run.
Configuration rules are meant to dynamically change gitlint's configuration and/or the commit that is about to be
linted.
A typically use-case for this is when you want to modify gitlint's behavior for all rules against a commit matching
specific circumstances.

!!! warning
    Configuration rules can drastically change the way gitlint behaves and are typically only needed for more advanced
    use-cases. We recommend you double check:

    1. Whether gitlint already supports your use-case out-of-the-box (special call-out for [ignore rules](../../ignoring_commits.md) which allow you to ignore (parts) of your commit message).
    2. Whether there's a [Contrib Rule](../contrib_rules.md) that implements your use-case.
    3. Whether you can implement your use-case using a [Commit or Line user-defined rule](line_and_commit_rules.md).


As with other user-defined rules, the easiest way to get started is by copying [`my_configuration.py` from the examples directory](https://github.com/jorisroovers/gitlint/tree/main/examples/my_configuration_rules.py) and modifying it to fit your need.

```{ .python .copy title="examples/my_configuration_rules.py" linenums="1"}
from gitlint.rules import ConfigurationRule
from gitlint.options import IntOption

class ReleaseConfigurationRule(ConfigurationRule):
    """
    This rule will modify gitlint's behavior for Release Commits.

    This example might not be the most realistic for a real-world scenario,
    but is meant to give an overview of what's possible.
    """

    # A rule MUST have a human friendly name
    name = "release-configuration-rule"

    # A rule MUST have a *unique* id
    # We recommend starting with UCR (for User-defined Configuration-Rule)
    id = "UCR1"

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [
        IntOption("custom-verbosity", 2, "Verbosity for release commits"),
    ]

    def apply(self, config, commit):
        self.log.debug("This will be visible when running `gitlint --debug`")

        # If the commit title starts with 'Release', we want to modify
        # how all subsequent rules interpret that commit
        if commit.message.title.startswith("Release"):

            # If your Release commit messages are auto-generated, the
            # body might contain trailing whitespace. Let's ignore that
            config.ignore.append("body-trailing-whitespace")

            # Similarly, the body lines might exceed 80 chars,
            # let's set gitlint's limit to 99
            # To set rule options use:
            # config.set_rule_option(<rule-name>, <rule-option>, <value>)
            config.set_rule_option("body-max-line-length", "line-length", 99)

            # For kicks, let's set gitlint's verbosity to 2
            # To set general options use
            # config.set_general_option(<general-option>, <value>)
            config.set_general_option("verbosity", 2)
            # We can also use custom options to make this configurable
            custom_verbosity = self.options["custom-verbosity"].value
            config.set_general_option("verbosity", custom_verbosity)

            # Strip any lines starting with $ from the commit message
            # (this only affects how gitlint sees your commit message,
            # it does NOT modify your actual commit in git)
            body = [l for l in commit.message.body if not l.startswith("$")]
            commit.message.body = body

            # You can add any extra properties you want to the commit object,
            # these will be available later on in all rules.
            commit.my_property = "This is my property"
```

For all available properties and methods on the `config` object, have a look at the
[LintConfig class](https://github.com/jorisroovers/gitlint/blob/main/gitlint-core/gitlint/config.py). Please do not use any
properties or methods starting with an underscore, as those are subject to change.
