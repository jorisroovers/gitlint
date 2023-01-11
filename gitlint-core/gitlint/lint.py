import logging

from gitlint import display
from gitlint import rules as gitlint_rules
from gitlint.deprecation import Deprecation

LOG = logging.getLogger(__name__)
logging.basicConfig()


class GitLinter:
    """Main linter class. This is where rules actually get applied. See the lint() method."""

    def __init__(self, config):
        self.config = config

        self.display = display.Display(config)

    def should_ignore_rule(self, rule):
        """Determines whether a rule should be ignored based on the general list of commits to ignore"""
        return rule.id in self.config.ignore or rule.name in self.config.ignore

    @property
    def configuration_rules(self):
        return [
            rule
            for rule in self.config.rules
            if isinstance(rule, gitlint_rules.ConfigurationRule) and not self.should_ignore_rule(rule)
        ]

    @property
    def title_line_rules(self):
        return [
            rule
            for rule in self.config.rules
            if isinstance(rule, gitlint_rules.LineRule)
            and rule.target == gitlint_rules.CommitMessageTitle
            and not self.should_ignore_rule(rule)
        ]

    @property
    def body_line_rules(self):
        return [
            rule
            for rule in self.config.rules
            if isinstance(rule, gitlint_rules.LineRule)
            and rule.target == gitlint_rules.CommitMessageBody
            and not self.should_ignore_rule(rule)
        ]

    @property
    def commit_rules(self):
        return [
            rule
            for rule in self.config.rules
            if isinstance(rule, gitlint_rules.CommitRule) and not self.should_ignore_rule(rule)
        ]

    @staticmethod
    def _apply_line_rules(lines, commit, rules, line_nr_start):
        """Iterates over the lines in a given list of lines and validates a given list of rules against each line"""
        all_violations = []
        line_nr = line_nr_start
        for line in lines:
            for rule in rules:
                violations = rule.validate(line, commit)
                if violations:
                    for violation in violations:
                        violation.line_nr = line_nr
                        all_violations.append(violation)
            line_nr += 1
        return all_violations

    @staticmethod
    def _apply_commit_rules(rules, commit):
        """Applies a set of rules against a given commit and gitcontext"""
        all_violations = []
        for rule in rules:
            violations = rule.validate(commit)
            if violations:
                all_violations.extend(violations)
        return all_violations

    def lint(self, commit):
        """Lint the last commit in a given git context by applying all ignore, title, body and commit rules."""
        LOG.debug("Linting commit %s", commit.sha or "[SHA UNKNOWN]")
        LOG.debug("Commit Object\n" + str(commit))

        # Ensure the Deprecation class has a reference to the config currently being used
        Deprecation.config = self.config

        # Apply config rules
        for rule in self.configuration_rules:
            rule.apply(self.config, commit)

        # Skip linting if this is a special commit type that is configured to be ignored
        ignore_commit_types = ["merge", "squash", "fixup", "fixup_amend", "revert"]
        for commit_type in ignore_commit_types:
            if getattr(commit, f"is_{commit_type}_commit") and getattr(self.config, f"ignore_{commit_type}_commits"):
                return []

        violations = []
        # determine violations by applying all rules
        violations.extend(self._apply_line_rules([commit.message.title], commit, self.title_line_rules, 1))
        violations.extend(self._apply_line_rules(commit.message.body, commit, self.body_line_rules, 2))
        violations.extend(self._apply_commit_rules(self.commit_rules, commit))

        # Sort violations by line number and rule_id. If there's no line nr specified (=common certain commit rules),
        # we replace None with -1 so that it always get's placed first. Note that we need this to do this to support
        # python 3, as None is not allowed in a list that is being sorted.
        violations.sort(key=lambda v: (-1 if v.line_nr is None else v.line_nr, v.rule_id))
        return violations

    def print_violations(self, violations):
        """Print a given set of violations to the standard error output"""
        for v in violations:
            line_nr = v.line_nr if v.line_nr else "-"
            self.display.e(f"{line_nr}: {v.rule_id}", exact=True)
            self.display.ee(f"{line_nr}: {v.rule_id} {v.message}", exact=True)
            if v.content:
                self.display.eee(f'{line_nr}: {v.rule_id} {v.message}: "{v.content}"', exact=True)
            else:
                self.display.eee(f"{line_nr}: {v.rule_id} {v.message}", exact=True)
