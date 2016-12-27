from gitlint import rules as gitlint_rules
from gitlint import display


class GitLinter(object):
    """ Main linter class. This is where rules actually get applied. See the lint() method. """

    def __init__(self, config):
        self.config = config

        self.display = display.Display(config)

    def ignore_rule(self, rule):
        return rule.id in self.config.ignore or rule.name in self.config.ignore

    @property
    def title_line_rules(self):
        return [rule for rule in self.config.rules if
                isinstance(rule, gitlint_rules.LineRule) and
                rule.target == gitlint_rules.CommitMessageTitle and not self.ignore_rule(rule)]

    @property
    def body_line_rules(self):
        return [rule for rule in self.config.rules if
                isinstance(rule, gitlint_rules.LineRule) and
                rule.target == gitlint_rules.CommitMessageBody and not self.ignore_rule(rule)]

    @property
    def commit_rules(self):
        return [rule for rule in self.config.rules if isinstance(rule, gitlint_rules.CommitRule) and
                not self.ignore_rule(rule)]

    @staticmethod
    def _apply_line_rules(lines, commit, rules, line_nr_start):
        """ Iterates over the lines in a given list of lines and validates a given list of rules against each line """
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
        """ Applies a set of rules against a given commit and gitcontext """
        all_violations = []
        for rule in rules:
            violations = rule.validate(commit)
            if violations:
                all_violations.extend(violations)
        return all_violations

    def lint(self, commit):
        """ Lint the last commit in a given git context by applying all title, body and general rules. """

        # Skip linting if this is merge commit and if the config is set to ignore those
        if commit.is_merge_commit and self.config.ignore_merge_commits:
            return []

        violations = []
        # determine violations by applying all rules
        violations.extend(self._apply_line_rules([commit.message.title], commit, self.title_line_rules, 1))
        violations.extend(self._apply_line_rules(commit.message.body, commit, self.body_line_rules, 2))
        violations.extend(self._apply_commit_rules(self.commit_rules, commit))

        # sort violations by line number
        violations.sort(key=lambda v: (v.line_nr, v.rule_id))  # sort violations by line number and rule_id
        return violations

    def print_violations(self, violations):
        """ Print a given set of violations to the standard error output """
        for v in violations:
            self.display.e(u"{0}: {1}".format(v.line_nr, v.rule_id), exact=True)
            self.display.ee(u"{0}: {1} {2}".format(v.line_nr, v.rule_id, v.message), exact=True)
            if v.content:
                self.display.eee(u"{0}: {1} {2}: \"{3}\"".format(v.line_nr, v.rule_id, v.message, v.content),
                                 exact=True)
            else:
                self.display.eee(u"{0}: {1} {2}".format(v.line_nr, v.rule_id, v.message), exact=True)
