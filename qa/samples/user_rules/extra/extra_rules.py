# -*- coding: utf-8 -*-

from gitlint.rules import CommitRule, RuleViolation, ConfigurationRule
from gitlint.options import IntOption, StrOption, ListOption


class GitContextRule(CommitRule):
    """ Rule that tests whether we can correctly access certain gitcontext properties """
    name = "gïtcontext"
    id = "UC1"

    def validate(self, commit):
        violations = [
            RuleViolation(self.id, "GitContext.current_branch: {0}".format(commit.context.current_branch), line_nr=1),
            RuleViolation(self.id, "GitContext.commentchar: {0}".format(commit.context.commentchar), line_nr=1)
        ]

        return violations


class GitCommitRule(CommitRule):
    """ Rule that tests whether we can correctly access certain commit properties """
    name = "gïtcommit"
    id = "UC2"

    def validate(self, commit):
        violations = [
            RuleViolation(self.id, "GitCommit.branches: {0}".format(commit.branches), line_nr=1),
            RuleViolation(self.id, "GitCommit.custom_prop: {0}".format(commit.custom_prop), line_nr=1),
        ]

        return violations


class GitlintConfigurationRule(ConfigurationRule):
    """ Rule that tests whether we can correctly access the config as well as modify the commit message """
    name = "cönfigrule"
    id = "UC3"

    def apply(self, config, commit):
        # We add a line to the commit message body that pulls a value from config, this proves we can modify the body
        # and read the config contents
        commit.message.body.append("{0} ".format(config.target))  # trailing whitespace deliberate to trigger violation

        # We set a custom property that we access in CommitRule, to prove we can add extra properties to the commit
        commit.custom_prop = "foöbar"

        # We also ignore some extra rules, proving that we can modify the config
        config.ignore.append("B4")


class ConfigurableCommitRule(CommitRule):
    """ Rule that tests that we can add configuration to user-defined rules """
    name = "configürable"
    id = "UC4"

    options_spec = [IntOption("int-öption", 2, "int-öption description"),
                    StrOption("str-öption", "föo", "int-öption description"),
                    ListOption("list-öption", ["foo", "bar"], "list-öption description")]

    def validate(self, _):
        violations = [
            RuleViolation(self.id, "int-öption: {0}".format(self.options[u'int-öption'].value), line_nr=1),
            RuleViolation(self.id, "str-öption: {0}".format(self.options[u'str-öption'].value), line_nr=1),
            RuleViolation(self.id, "list-öption: {0}".format(self.options[u'list-öption'].value), line_nr=1),
        ]

        return violations
