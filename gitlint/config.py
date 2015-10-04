from gitlint import rules
from gitlint import options

try:
    # python 2.x
    import ConfigParser
except ImportError:  # pragma: no cover
    # python 3.x
    from configparser import ConfigParser  # pragma: no cover
from collections import OrderedDict
import re
import os


class LintConfigError(Exception):
    pass


class LintConfig(object):
    """ Class representing gitlint configuration """
    default_rule_classes = [rules.TitleMaxLength,
                            rules.TitleTrailingWhitespace,
                            rules.TitleLeadingWhitespace,
                            rules.TitleTrailingPunctuation,
                            rules.TitleHardTab,
                            rules.TitleMustNotContainWord,
                            rules.TitleRegexMatches,
                            rules.BodyMaxLineLength,
                            rules.BodyMinLength,
                            rules.BodyMissing,
                            rules.BodyTrailingWhitespace,
                            rules.BodyHardTab,
                            rules.BodyFirstLineEmpty,
                            rules.BodyChangedFileMention]

    def __init__(self, config_path=None):
        # Use an ordered dict so that the order in which rules are applied is always the same
        self._rules = OrderedDict([(rule_cls.id, rule_cls()) for rule_cls in self.default_rule_classes])
        self._verbosity = 3
        self.config_path = config_path

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        if value < 0 or value > 3:
            raise LintConfigError("verbosity must be set between 0 and 3")
        self._verbosity = value

    @property
    def rules(self):
        return [rule for rule in self._rules.values()]

    @property
    def body_rules(self):
        return [rule for rule in self._rules.values() if isinstance(rule, rules.CommitMessageBodyRule)]

    @property
    def title_rules(self):
        return [rule for rule in self._rules.values() if isinstance(rule, rules.CommitMessageTitleRule)]

    def disable_rule_by_id(self, rule_id):
        del self._rules[rule_id]

    def disable_rule(self, rule_id_or_name):
        if rule_id_or_name == "all":
            self._rules = OrderedDict()
        else:
            rule = self.get_rule(rule_id_or_name)
            if rule:
                self.disable_rule_by_id(rule.id)

    def get_rule(self, rule_id_or_name):
        # try finding rule by id
        rule = self._rules.get(rule_id_or_name)
        # if not found, try finding rule by name
        if not rule:
            rule = next((rule for rule in self._rules.values() if rule.name == rule_id_or_name), None)
        return rule

    def _get_option(self, rule_name_or_id, option_name):
        rule = self.get_rule(rule_name_or_id)
        if not rule:
            raise LintConfigError("No such rule '{}'".format(rule_name_or_id))

        option = rule.options.get(option_name)
        if not option:
            raise LintConfigError("Rule '{}' has no option '{}'".format(rule_name_or_id, option_name))

        return option

    def get_rule_option(self, rule_name_or_id, option_name):
        """ Returns the value of a given option for a given rule. LintConfigErrors will be raised if the
        rule or option don't exist. """
        option = self._get_option(rule_name_or_id, option_name)
        return option.value

    def set_rule_option(self, rule_name_or_id, option_name, option_value):
        """ Attempts to set a given value for a given option for a given rule.
            LintConfigErrors will be raised if the rule or option don't exist or if the value is invalid. """
        option = self._get_option(rule_name_or_id, option_name)
        try:
            option.set(option_value)
        except options.RuleOptionError as e:
            raise LintConfigError(
                "'{}' is not a valid value for option '{}.{}'. {}.".format(option_value, rule_name_or_id, option_name,
                                                                           e.message))

    def apply_config_from_gitcontext(self, gitcontext):
        """ Given a git context, applies config specified in the commit message.
            Supported:
             - gitlint: disable
        """
        for line in gitcontext.commit_msg.full.split("\n"):
            pattern = re.compile(r"^gitlint-ignore:\s*(.*)")
            matches = pattern.match(line)
            if matches and len(matches.groups()) == 1:
                self.set_general_option('ignore', matches.group(1))
                self.enabled = False

    def apply_config_options(self, config_options):
        """ Given a list of config options of the form "<rule>.<option>=<value>", parses out the correct rule and option
        and sets the value accordingly in this config object. """
        for config_option in config_options:
            try:
                config_name, option_value = config_option.split("=", 1)
                if not option_value:
                    raise ValueError()
                rule_name, option_name = config_name.split(".", 1)
                if rule_name == "general":
                    self.set_general_option(option_name, option_value)
                else:
                    self.set_rule_option(rule_name, option_name, option_value)
            except ValueError:  # raised if the config string is invalid
                raise LintConfigError(
                    "'{}' is an invalid configuration option. Use '<rule>.<option>=<value>'".format(config_option))

    def set_general_option(self, option_name, option_value):
        if option_name == "ignore":
            self.apply_on_csv_string(option_value, self.disable_rule)
        elif option_name == "verbosity":
            self.verbosity = int(option_value)

    @staticmethod
    def apply_on_csv_string(rules_str, func):
        """ Splits a given string by comma, trims whitespace on the resulting strings and applies a given ```func``` to
        each item. """
        splitted = rules_str.split(",")
        for str in splitted:
            func(str.strip())

    @staticmethod
    def load_from_file(filename):
        """ Loads lint config from a ini-style config file """
        if not os.path.exists(filename):
            raise LintConfigError("Invalid file path: {0}".format(filename))
        config = LintConfig(config_path=os.path.abspath(filename))
        try:
            parser = ConfigParser.ConfigParser()
            parser.read(filename)
            LintConfig._parse_general_section(parser, config)
            LintConfig._parse_rule_sections(parser, config)
        except ConfigParser.Error as e:
            raise LintConfigError(e.message)

        return config

    @staticmethod
    def _parse_rule_sections(parser, config):
        sections = [section for section in parser.sections() if section != "general"]
        for rule_name in sections:
            for option_name, option_value in parser.items(rule_name):
                config.set_rule_option(rule_name, option_name, option_value)

    @staticmethod
    def _parse_general_section(parser, config):
        if parser.has_section('general'):
            for option_name, option_value in parser.items('general'):
                config.set_general_option(option_name, option_value)
