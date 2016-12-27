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

from gitlint.utils import ustr
from gitlint import rules  # For some weird reason pylint complains about this, pylint: disable=unused-import
from gitlint import options
from gitlint import user_rules


def handle_option_error(func):
    """ Decorator that calls given method/function and handles any RuleOptionError gracefully by converting it to a
    LintConfigError. """

    def wrapped(*args):
        try:
            return func(*args)
        except options.RuleOptionError as e:
            raise LintConfigError(ustr(e))

    return wrapped


class LintConfigError(Exception):
    pass


class LintConfig(object):
    """ Class representing gitlint configuration.
        Contains active config as well as number of methods to easily get/set the config.
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
        self._ignore = options.ListOption('ignore', [], 'List of rule-ids to ignore')
        self._config_path = None

    @property
    def target(self):
        return self._target.value if self._target else None

    @target.setter
    @handle_option_error
    def target(self, value):
        return self._target.set(value)

    @property
    def verbosity(self):
        return self._verbosity.value

    @verbosity.setter
    @handle_option_error
    def verbosity(self, value):
        self._verbosity.set(value)
        if self.verbosity < 0 or self.verbosity > 3:
            raise LintConfigError("Option 'verbosity' must be set between 0 and 3")

    @property
    def ignore_merge_commits(self):
        return self._ignore_merge_commits.value

    @ignore_merge_commits.setter
    @handle_option_error
    def ignore_merge_commits(self, value):
        return self._ignore_merge_commits.set(value)

    @property
    def debug(self):
        return self._debug.value

    @debug.setter
    @handle_option_error
    def debug(self, value):
        return self._debug.set(value)

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

        except (options.RuleOptionError, user_rules.UserRuleError) as e:
            raise LintConfigError(ustr(e))

    @property
    def ignore(self):
        return self._ignore.value

    @ignore.setter
    def ignore(self, value):
        if value == "all":
            value = [rule.id for rule in self.rules]
        return self._ignore.set(value)

    @property
    def rules(self):
        # Create a new list based on _rules.values() because in python 3, values() is a ValuesView as opposed to a list
        return [rule for rule in self._rules.values()]

    def get_rule(self, rule_id_or_name):
        # try finding rule by id
        rule_id_or_name = ustr(rule_id_or_name)  # convert to unicode first
        rule = self._rules.get(rule_id_or_name)
        # if not found, try finding rule by name
        if not rule:
            rule = next((rule for rule in self._rules.values() if rule.name == rule_id_or_name), None)
        return rule

    def _get_option(self, rule_name_or_id, option_name):
        rule_name_or_id = ustr(rule_name_or_id)  # convert to unicode first
        option_name = ustr(option_name)
        rule = self.get_rule(rule_name_or_id)
        if not rule:
            raise LintConfigError(u"No such rule '{0}'".format(rule_name_or_id))

        option = rule.options.get(option_name)
        if not option:
            raise LintConfigError(u"Rule '{0}' has no option '{1}'".format(rule_name_or_id, option_name))

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
            msg = u"'{0}' is not a valid value for option '{1}.{2}'. {3}."
            raise LintConfigError(msg.format(option_value, rule_name_or_id, option_name, ustr(e)))

    def set_general_option(self, option_name, option_value):
        attr_name = option_name.replace("-", "_")
        # only allow setting general options that exist and don't start with an underscore
        if not hasattr(self, attr_name) or attr_name[0] == "_":
            raise LintConfigError(u"'{0}' is not a valid gitlint option".format(option_name))
        else:
            setattr(self, attr_name, option_value)

    def __eq__(self, other):
        return isinstance(other, LintConfig) and \
               self.rules == other.rules and \
               self.verbosity == other.verbosity and \
               self.target == other.target and \
               self.extra_path == other.extra_path and \
               self.ignore_merge_commits == other.ignore_merge_commits and \
               self.debug == other.debug and \
               self.ignore == other.ignore and \
               self._config_path == other._config_path  # noqa

    def __str__(self):
        # config-path is not a user exposed variable, so don't print it under the general section
        return_str = u"config-path: {0}\n".format(self._config_path)
        return_str += u"[GENERAL]\n"
        return_str += u"extra-path: {0}\n".format(self.extra_path)
        return_str += u"ignore: {0}\n".format(",".join(self.ignore))
        return_str += u"ignore-merge-commits: {0}\n".format(self.ignore_merge_commits)
        return_str += u"verbosity: {0}\n".format(self.verbosity)
        return_str += u"debug: {0}\n".format(self.debug)
        return_str += u"target: {0}\n".format(self.target)
        return_str += u"[RULES]\n"
        for rule in self.rules:
            return_str += u"  {0}: {1}\n".format(rule.id, rule.name)
            for option_name, option_value in rule.options.items():
                if isinstance(option_value.value, list):
                    option_val_repr = ",".join(option_value.value)
                else:
                    option_val_repr = option_value.value
                return_str += u"     {0}={1}\n".format(option_name, option_val_repr)
        return return_str


class LintConfigBuilder(object):
    """ Factory class that can build gitlint config.
    This is primarily useful to deal with complex configuration scenarios where configuration can be set and overridden
    from various sources (typically according to certain precedence rules) before the actual config should be
    normalized, validated and build. Example usage can be found in gitlint.cli.
    """

    def __init__(self):
        self._config_blueprint = {}
        self._config_path = None

    def set_option(self, section, option_name, option_value):
        if section not in self._config_blueprint:
            self._config_blueprint[section] = {}
        self._config_blueprint[section][option_name] = option_value

    def set_config_from_commit(self, commit):
        """ Given a git commit, applies config specified in the commit message.
            Supported:
             - gitlint-ignore: all
        """
        for line in commit.message.full.split("\n"):
            pattern = re.compile(r"^gitlint-ignore:\s*(.*)")
            matches = pattern.match(line)
            if matches and len(matches.groups()) == 1:
                self.set_option('general', 'ignore', matches.group(1))

    def set_config_from_string_list(self, config_options):
        """ Given a list of config options of the form "<rule>.<option>=<value>", parses out the correct rule and option
        and sets the value accordingly in this factory object. """
        for config_option in config_options:
            try:
                config_name, option_value = config_option.split("=", 1)
                if not option_value:
                    raise ValueError()
                rule_name, option_name = config_name.split(".", 1)
                self.set_option(rule_name, option_name, option_value)
            except ValueError:  # raised if the config string is invalid
                raise LintConfigError(
                    u"'{0}' is an invalid configuration option. Use '<rule>.<option>=<value>'".format(config_option))

    def set_from_config_file(self, filename):
        """ Loads lint config from a ini-style config file """
        if not os.path.exists(filename):
            raise LintConfigError(u"Invalid file path: {0}".format(filename))
        self._config_path = os.path.abspath(filename)
        try:
            parser = ConfigParser()
            parser.read(filename)

            for section_name in parser.sections():
                for option_name, option_value in parser.items(section_name):
                    self.set_option(section_name, option_name, ustr(option_value))

        except ConfigParserError as e:
            raise LintConfigError(ustr(e))

    def build(self, config=None):
        """ Build a real LintConfig object by normalizing and validating the options that were previously set on this
        factory. """

        # If we are passed a config object, then rebuild that object instead of building a new lintconfig object from
        # scratch
        if not config:
            config = LintConfig()

        config._config_path = self._config_path

        # Set general options first as this might change the behavior or validity of the other options
        general_section = self._config_blueprint.get('general')
        if general_section:
            for option_name, option_value in general_section.items():
                config.set_general_option(option_name, option_value)

        for section_name, section_dict in self._config_blueprint.items():
            for option_name, option_value in section_dict.items():
                # Skip over the general section, as we've already done that above
                if section_name != "general":
                    config.set_rule_option(section_name, option_name, option_value)

        return config


GITLINT_CONFIG_TEMPLATE_SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/gitlint")


class LintConfigGenerator(object):
    @staticmethod
    def generate_config(dest):
        """ Generates a gitlint config file at the given destination location.
            Expects that the given ```dest``` points to a valid destination. """
        shutil.copyfile(GITLINT_CONFIG_TEMPLATE_SRC_PATH, dest)
