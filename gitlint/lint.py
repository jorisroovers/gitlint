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

    def lint(self, string):
        all_violations = []
        all_violations.extend(self._apply_line_rules(string))
        return all_violations

    def lint_files(self, files):
        """ Lints a list of files.
        :param files: list of files to lint
        :return: a list of violations found in the files
        """
        all_violations = []
        for filename in files:
            with open(filename, 'r') as f:
                content = f.read()
                violations = self.lint(content)
                all_violations.extend(violations)
                for e in violations:
                    print("{0}:{1}: {2} {3}".format(filename, e.line_nr, e.rule_id, e.message))
        return len(all_violations)
