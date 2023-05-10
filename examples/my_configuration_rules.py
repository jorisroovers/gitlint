from gitlint.rules import ConfigurationRule
from gitlint.options import IntOption


"""
Full details on user-defined rules: https://jorisroovers.github.io/gitlint/user_defined_rules

The ReleaseConfigurationRule class below is an example of a user-defined ConfigurationRule. Configuration rules are
gitlint rules that are applied once per commit and BEFORE any other rules are run. Configuration Rules are meant to
dynamically change gitlint's configuration and/or the commit that is about to be linted. A typically use-case for this
is modifying the behavior of gitlint's rules based on a commit contents.

Notes:
- Modifying the commit object DOES NOT modify the actual git commit message in the target repo, only gitlint's copy of
  it.
- Modifying the config object only has effect on the commit that is being linted, subsequent commits will not
  automatically inherit this configuration.
"""


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
            # let's set gitlint's limit to 200
            # To set rule options use:
            # config.set_rule_option(<rule-name>, <rule-option>, <value>)
            config.set_rule_option("body-max-line-length", "line-length", 200)

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
