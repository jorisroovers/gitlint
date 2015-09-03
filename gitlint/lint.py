from __future__ import print_function
from gitlint import rules


class GitLinter(object):
    def __init__(self, config):
        self.config = config

    @property
    def line_rules(self):
        return [rule for rule in self.config.rules if isinstance(rule, rules.LineRule)]

    def _apply_line_rules(self, commit_message):
        """ Iterates over the lines in a given git commit message and applies all the enabled line rules to
        each line """
        all_violations = []
        lines = commit_message.split("\n")
        line_rules = self.line_rules
        line_nr = 1
        for line in lines:
            for rule in line_rules:
                violation = rule.validate(line)
                if violation:
                    violation.line_nr = line_nr
                    all_violations.append(violation)
            line_nr += 1
        return all_violations

    def lint_commit_message(self, commit_message):
        violations = self._apply_line_rules(commit_message)
        for v in violations:
            print("{}: {} {}: \"{}\"".format(v.line_nr, v.rule_id, v.message, v.content))
        return len(violations)
