from gitlint import rules
import ConfigParser
from collections import OrderedDict

import os


class LintConfigError(Exception):
    pass


class LintConfig(object):
    """ Class representing gitlint configuration """
    default_rule_classes = [rules.TitleMaxLengthRule, rules.TitleTrailingWhitespace, rules.TitleHardTab,
                            rules.BodyMaxLengthRule, rules.BodyTrailingWhitespace, rules.BodyHardTab]

    def __init__(self):
        # Use an ordered dict so that the order in which rules are applied is always the same
        self._rules = OrderedDict([(rule_cls.id, rule_cls()) for rule_cls in self.default_rule_classes])

    @property
    def body_rules(self):
        return [rule for rule in self._rules.values() if isinstance(rule, rules.CommitMessageBodyRule)]

    @property
    def title_rules(self):
        return [rule for rule in self._rules.values() if isinstance(rule, rules.CommitMessageTitleRule)]

    def disable_rule_by_id(self, rule_id):
        del self._rules[rule_id]

    def get_rule_by_name_or_id(self, rule_id_or_name):
        # try finding rule by id
        rule = self._rules.get(rule_id_or_name)
        # if not found, try finding rule by name
        if not rule:
            rule = next((rule for rule in self._rules.values() if rule.name == rule_id_or_name), None)
        return rule

    def disable_rule(self, rule_id_or_name):
        rule = self.get_rule_by_name_or_id(rule_id_or_name)
        if rule:
            self.disable_rule_by_id(rule.id)

    @staticmethod
    def apply_on_csv_string(rules_str, func):
        """ Splits a given string by comma, trims whitespace on the resulting strings and applies a given ```func``` to
        each item. """
        splitted = rules_str.split(",")
        for str in splitted:
            func(str.strip())

    @staticmethod
    def load_from_file(filename):
        if not os.path.exists(filename):
            raise LintConfigError("Invalid file path: {0}".format(filename))
        config = LintConfig()
        try:
            parser = ConfigParser.ConfigParser()
            parser.read(filename)
            LintConfig._parse_general_section(parser, config)
        except ConfigParser.Error as e:
            raise LintConfigError("Error during config file parsing: {0}".format(e.message))

        return config

    @staticmethod
    def _parse_general_section(parser, config):
        if parser.has_section('general'):
            ignore = parser.get('general', 'ignore', "")
            LintConfig.apply_on_csv_string(ignore, config.disable_rule)
