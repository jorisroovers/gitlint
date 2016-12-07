try:
    # python 2.x
    from ConfigParser import ConfigParser, Error as ConfigParserError
except ImportError:  # pragma: no cover
    # python 3.x
    from configparser import ConfigParser, Error as ConfigParserError  # pragma: no cover, pylint: disable=import-error

import re
import os
import shutil

try:
    # python >= 2.7
    from collections import OrderedDict  # pylint: disable=no-name-in-module
except ImportError:  # pragma: no cover
    # python 2.4-2.6
    from ordereddict import OrderedDict  # pragma: no cover

from gitlint import rules  # For some weird reason pylint complains about this, pylint: disable=unused-import
from gitlint import options
from gitlint import user_rules


class LintConfigError(Exception):
    pass


class LintConfig(object):
    """ Class representing gitlint configuration.
        Contains active config as well as number of methods to easily get/set the config
        (such as reading it from file or parsing commandline input).
    """

    # Default tuple of rule classes (tuple because immutable).
    default_rule_classes = (rules.TitleMaxLength,
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
                            rules.BodyChangedFileMention)

    def __init__(self):
        # Use an ordered dict so that the order in which rules are applied is always the same
        self._rules = OrderedDict([(rule_cls.id, rule_cls()) for rule_cls in self.default_rule_classes])
        self._verbosity = options.IntOption('verbosity', 3, "Verbosity")
        self._ignore_merge_commits = options.BoolOption('ignore-merge-commits', True, "Ignore merge commits")
        self._debug = options.BoolOption('debug', False, "Enable debug mode")
        self._extra_path = None
        target_description = "Path of the target git repository (default=current working directory)"
        self._target = options.DirectoryOption('target', os.path.abspath(os.getcwd()), target_description)

        self._config_path = None

    @property
    def target(self):
        return self._target.value if self._target else None

    @target.setter
    def target(self, value):
        try:
            return self._target.set(value)
        except options.RuleOptionError as e:
            raise LintConfigError(str(e))

    @property
    def verbosity(self):
        return self._verbosity.value

    @verbosity.setter
    def verbosity(self, value):
        try:
            self._verbosity.set(value)
            if self.verbosity < 0 or self.verbosity > 3:
                raise LintConfigError("Option 'verbosity' must be set between 0 and 3")
        except options.RuleOptionError as e:
            raise LintConfigError(str(e))

    @property
    def ignore_merge_commits(self):
        return self._ignore_merge_commits.value

    @ignore_merge_commits.setter
    def ignore_merge_commits(self, value):
        try:
            return self._ignore_merge_commits.set(value)
        except options.RuleOptionError as e:
            raise LintConfigError(str(e))

    @property
    def debug(self):
        return self._debug.value

    @debug.setter
    def debug(self, value):
        try:
            return self._debug.set(value)
        except options.RuleOptionError as e:
            raise LintConfigError(str(e))

    @property
    def extra_path(self):
        return self._extra_path.value if self._extra_path else None

    @extra_path.setter
    def extra_path(self, value):
        try:
            if self.extra_path:
                self._extra_path.set(value)
            else:
                self._extra_path = options.DirectoryOption('extra-path', value,
                                                           "Path to a directory with extra user-defined rules")

            # Make sure we unload any previously loaded extra-path rules
            for rule in self.rules:
                if hasattr(rule, 'user_defined') and rule.user_defined:
                    del self._rules[rule.id]

            # Find rules in the new extra-path
            rule_classes = user_rules.find_rule_classes(self.extra_path)

            # Add the newly found rules to the existing rules
            for rule_class in rule_classes:
                rule_obj = rule_class()
                rule_obj.user_defined = True
                self._rules[rule_class.id] = rule_obj

        except options.RuleOptionError as e:
            raise LintConfigError(str(e))
        except Exception as e:
            # TODO(joris.roovers): better error message
            raise e

    @property
    def rules(self):
        # Create a new list based on _rules.values() because in python 3, values() is a ValuesView as opposed to a list
        return [rule for rule in self._rules.values()]

    def disable_rule(self, rule_id_or_name):
        if rule_id_or_name == "all":
            self._rules = OrderedDict()
        else:
            rule = self.get_rule(rule_id_or_name)
            if rule:
                del self._rules[rule.id]

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
            raise LintConfigError("No such rule '{0}'".format(rule_name_or_id))

        option = rule.options.get(option_name)
        if not option:
            raise LintConfigError("Rule '{0}' has no option '{1}'".format(rule_name_or_id, option_name))

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
                "'{0}' is not a valid value for option '{1}.{2}'. {3}.".format(option_value, rule_name_or_id,
                                                                               option_name, str(e)))

    def apply_config_from_commit(self, commit):
        """ Given a git commit, applies config specified in the commit message.
            Supported:
             - gitlint-ignore: all
        """
        for line in commit.message.full.split("\n"):
            pattern = re.compile(r"^gitlint-ignore:\s*(.*)")
            matches = pattern.match(line)
            if matches and len(matches.groups()) == 1:
                self.set_general_option('ignore', matches.group(1))

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
                    "'{0}' is an invalid configuration option. Use '<rule>.<option>=<value>'".format(config_option))

    def set_general_option(self, option_name, option_value):
        if option_name == "ignore":
            self.apply_on_csv_string(option_value, self.disable_rule)
        else:
            attr_name = option_name.replace("-", "_")
            # only allow setting general options that exist and don't start with an underscore
            if not hasattr(self, attr_name) or attr_name[0] == "_":
                raise LintConfigError("'{0}' is not a valid gitlint option".format(option_name))
            else:
                setattr(self, attr_name, option_value)

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
        config = LintConfig()
        config._config_path = os.path.abspath(filename)
        try:
            parser = ConfigParser()
            parser.read(filename)
            # Note: its important to parse the general section first as that might influence the parsing of the
            # rule-specific sections (e.g. extra rules with extra-path)
            LintConfig._parse_general_section(parser, config)
            LintConfig._parse_rule_sections(parser, config)
        except ConfigParserError as e:
            raise LintConfigError(str(e))

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

    def __eq__(self, other):
        return self.rules == other.rules and \
               self.verbosity == other.verbosity and \
               self.target == other.target and \
               self.extra_path == other.extra_path and \
               self.ignore_merge_commits == other.ignore_merge_commits and \
               self.debug == other.debug and \
               self._config_path == other._config_path  # noqa

    def __str__(self):
        # config-path is not a user exposed variable, so don't print it under the general section
        return_str = "config-path: {0}\n".format(self._config_path)
        return_str += "[GENERAL]\n"
        return_str += "extra-path: {0}\n".format(self.extra_path)
        return_str += "ignore-merge-commits: {0}\n".format(self.ignore_merge_commits)
        return_str += "verbosity: {0}\n".format(self.verbosity)
        return_str += "debug: {0}\n".format(self.debug)
        return_str += "target: {0}\n".format(self.target)
        return_str += "[RULES]\n"
        for rule in self.rules:
            return_str += "  {0}: {1}\n".format(rule.id, rule.name)
            for option_name, option_value in rule.options.items():
                return_str += "     {0}={1}\n".format(option_name, option_value.value)
        return return_str


GITLINT_CONFIG_TEMPLATE_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/gitlint")


class LintConfigGenerator(object):
    @staticmethod
    def generate_config(dest):
        """ Generates a gitlint config file at the given destination location.
            Expects that the given ```dest``` points to a valid destination. """
        shutil.copyfile(GITLINT_CONFIG_TEMPLATE_SRC_PATH, dest)
