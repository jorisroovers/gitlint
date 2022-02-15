# pylint: disable=logging-not-lazy
import copy
import logging
from gitlint import rules as gitlint_rules
from gitlint import display

LOG = logging.getLogger(__name__)
logging.basicConfig()


# TODO: should these utility methods move to gitlint.config.RuleCollection or to gitlint.config.Config?
def should_ignore_rule(rule, config):
    """ Determines whether a rule should be ignored based on the general list of commits to ignore """
    return rule.id in config.ignore or rule.name in config.ignore


def line_configuration_rules(config):
    return [rule for rule in config.rules if
            isinstance(rule, gitlint_rules.ConfigurationRule) and 
            hasattr(rule, 'target') and rule.target == gitlint_rules.Line and not should_ignore_rule(rule, config)]


def commit_configuration_rules(config):
    return [rule for rule in config.rules if
            isinstance(rule, gitlint_rules.ConfigurationRule) and
            (not hasattr(rule, 'target') or rule.target == gitlint_rules.Commit) and
            not should_ignore_rule(rule, config)]


def title_line_rules(config):
    return [rule for rule in config.rules if
            isinstance(rule, gitlint_rules.LineRule) and
            rule.target == gitlint_rules.CommitMessageTitle and not should_ignore_rule(rule, config)]


def body_line_rules(config):
    return [rule for rule in config.rules if
            isinstance(rule, gitlint_rules.LineRule) and
            rule.target == gitlint_rules.CommitMessageBody and not should_ignore_rule(rule, config)]


def commit_rules(config):
    return [rule for rule in config.rules if isinstance(rule, gitlint_rules.CommitRule) and
            not should_ignore_rule(rule, config)]

class GitLinter:
    """ Main linter class. This is where rules actually get applied. See the lint() method. """

    def __init__(self, config):
        self.config = config
        self.display = display.Display(config)

    def _apply_line_rules(self, lines, commit, rules_func, line_nr_start):
        """ Iterates over the lines in a given list of lines and validates a given list of rules against each line """
        all_violations = []
        line_nr = line_nr_start
        for line in lines:
            # Apply line configuration rules
            config = copy.deepcopy(self.config)
            for rule in line_configuration_rules(config):
                rule.apply(config, line)
            
            for rule in rules_func(config):
                violations = rule.validate(line, commit)
                if violations:
                    for violation in violations:
                        violation.line_nr = line_nr
                        all_violations.append(violation)
            line_nr += 1
        return all_violations

    @staticmethod
    def _apply_commit_rules(rules, commit):
        """ Applies a set of rules against a given commit and gitcontext """
        all_violations = []
        for rule in rules:
            violations = rule.validate(commit)
            if violations:
                all_violations.extend(violations)
        return all_violations

    def lint(self, commit):
        """ Lint the last commit in a given git context by applying all ignore, title, body and commit rules. """
        LOG.debug("Linting commit %s", commit.sha or "[SHA UNKNOWN]")
        LOG.debug("Commit Object\n" + str(commit))

        # Apply commit config rules
        for rule in commit_configuration_rules(self.config):
            rule.apply(self.config, commit)

        # Skip linting if this is a special commit type that is configured to be ignored
        ignore_commit_types = ["merge", "squash", "fixup", "revert"]
        for commit_type in ignore_commit_types:
            if getattr(commit, f"is_{commit_type}_commit") and \
               getattr(self.config, f"ignore_{commit_type}_commits"):
                return []

        violations = []
        # determine violations by applying all rules
        violations.extend(self._apply_line_rules([commit.message.title], commit, title_line_rules, 1))
        violations.extend(self._apply_line_rules(commit.message.body, commit, body_line_rules, 2))
        violations.extend(self._apply_commit_rules(commit_rules(self.config), commit))

        # Sort violations by line number and rule_id. If there's no line nr specified (=common certain commit rules),
        # we replace None with -1 so that it always get's placed first. Note that we need this to do this to support
        # python 3, as None is not allowed in a list that is being sorted.
        violations.sort(key=lambda v: (-1 if v.line_nr is None else v.line_nr, v.rule_id))
        return violations

    def print_violations(self, violations):
        """ Print a given set of violations to the standard error output """
        for v in violations:
            line_nr = v.line_nr if v.line_nr else "-"
            self.display.e(f"{line_nr}: {v.rule_id}", exact=True)
            self.display.ee(f"{line_nr}: {v.rule_id} {v.message}", exact=True)
            if v.content:
                self.display.eee(f"{line_nr}: {v.rule_id} {v.message}: \"{v.content}\"", exact=True)
            else:
                self.display.eee(f"{line_nr}: {v.rule_id} {v.message}", exact=True)
