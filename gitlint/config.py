try:
    # python 2.x
    from ConfigParser import ConfigParser, Error as ConfigParserError
except ImportError:  # pragma: no cover
    # python 3.x
    from configparser import ConfigParser, Error as ConfigParserError  # pragma: no cover, pylint: disable=import-error

import copy
import io
import re
import os
import shutil

from collections import OrderedDict
from gitlint.utils import ustr, DEFAULT_ENCODING
from gitlint import rules  # For some weird reason pylint complains about this, pylint: disable=unused-import
from gitlint import options
from gitlint import rule_finder
from gitlint.contrib import rules as contrib_rules


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
    default_rule_classes = (rules.IgnoreByTitle,
                            rules.IgnoreByBody,
                            rules.TitleMaxLength,
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
                            rules.BodyChangedFileMention,
                            rules.AuthorValidEmail)

    def __init__(self):
        self.rules = RuleCollection(self.default_rule_classes)
        self._verbosity = options.IntOption('verbosity', 3, "Verbosity")
        self._ignore_merge_commits = options.BoolOption('ignore-merge-commits', True, "Ignore merge commits")
        self._ignore_fixup_commits = options.BoolOption('ignore-fixup-commits', True, "Ignore fixup commits")
        self._ignore_squash_commits = options.BoolOption('ignore-squash-commits', True, "Ignore squash commits")
        self._ignore_revert_commits = options.BoolOption('ignore-revert-commits', True, "Ignore revert commits")
        self._debug = options.BoolOption('debug', False, "Enable debug mode")
        self._extra_path = None
        target_description = "Path of the target git repository (default=current working directory)"
        self._target = options.PathOption('target', os.path.realpath(os.getcwd()), target_description)
        self._ignore = options.ListOption('ignore', [], 'List of rule-ids to ignore')
        self._contrib = options.ListOption('contrib', [], 'List of contrib-rules to enable')
        self._config_path = None
        ignore_stdin_description = "Ignore any stdin data. Useful for running in CI server."
        self._ignore_stdin = options.BoolOption('ignore-stdin', False, ignore_stdin_description)
        self._staged = options.BoolOption('staged', False, "Read staged commit meta-info from the local repository.")

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
    def ignore_fixup_commits(self):
        return self._ignore_fixup_commits.value

    @ignore_fixup_commits.setter
    @handle_option_error
    def ignore_fixup_commits(self, value):
        return self._ignore_fixup_commits.set(value)

    @property
    def ignore_squash_commits(self):
        return self._ignore_squash_commits.value

    @ignore_squash_commits.setter
    @handle_option_error
    def ignore_squash_commits(self, value):
        return self._ignore_squash_commits.set(value)

    @property
    def ignore_revert_commits(self):
        return self._ignore_revert_commits.value

    @ignore_revert_commits.setter
    @handle_option_error
    def ignore_revert_commits(self, value):
        return self._ignore_revert_commits.set(value)

    @property
    def debug(self):
        return self._debug.value

    @debug.setter
    @handle_option_error
    def debug(self, value):
        return self._debug.set(value)

    @property
    def ignore(self):
        return self._ignore.value

    @ignore.setter
    def ignore(self, value):
        if value == "all":
            value = [rule.id for rule in self.rules]
        return self._ignore.set(value)

    @property
    def ignore_stdin(self):
        return self._ignore_stdin.value

    @ignore_stdin.setter
    @handle_option_error
    def ignore_stdin(self, value):
        return self._ignore_stdin.set(value)

    @property
    def staged(self):
        return self._staged.value

    @staged.setter
    @handle_option_error
    def staged(self, value):
        return self._staged.set(value)

    @property
    def extra_path(self):
        return self._extra_path.value if self._extra_path else None

    @extra_path.setter
    def extra_path(self, value):
        try:
            if self.extra_path:
                self._extra_path.set(value)
            else:
                self._extra_path = options.PathOption(
                    'extra-path', value,
                    "Path to a directory or module with extra user-defined rules",
                    type='both'
                )

            # Make sure we unload any previously loaded extra-path rules
            self.rules.delete_rules_by_attr("is_user_defined", True)

            # Find rules in the new extra-path and add them to the existing rules
            rule_classes = rule_finder.find_rule_classes(self.extra_path)
            self.rules.add_rules(rule_classes, {'is_user_defined': True})

        except (options.RuleOptionError, rules.UserRuleError) as e:
            raise LintConfigError(ustr(e))

    @property
    def contrib(self):
        return self._contrib.value

    @contrib.setter
    def contrib(self, value):
        try:
            self._contrib.set(value)

            # Make sure we unload any previously loaded contrib rules when re-setting the value
            self.rules.delete_rules_by_attr("is_contrib", True)

            # Load all classes from the contrib directory
            contrib_dir_path = os.path.dirname(os.path.realpath(contrib_rules.__file__))
            rule_classes = rule_finder.find_rule_classes(contrib_dir_path)

            # For each specified contrib rule, check whether it exists among the contrib classes
            for rule_id_or_name in self.contrib:
                rule_class = next((rc for rc in rule_classes if
                                   rc.id == ustr(rule_id_or_name) or rc.name == ustr(rule_id_or_name)), False)

                # If contrib rule exists, instantiate it and add it to the rules list
                if rule_class:
                    self.rules.add_rule(rule_class, rule_class.id, {'is_contrib': True})
                else:
                    raise LintConfigError(u"No contrib rule with id or name '{0}' found.".format(ustr(rule_id_or_name)))

        except (options.RuleOptionError, rules.UserRuleError) as e:
            raise LintConfigError(ustr(e))

    def _get_option(self, rule_name_or_id, option_name):
        rule_name_or_id = ustr(rule_name_or_id)  # convert to unicode first
        option_name = ustr(option_name)
        rule = self.rules.find_rule(rule_name_or_id)
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

        # else:
        setattr(self, attr_name, option_value)

    def __eq__(self, other):
        return isinstance(other, LintConfig) and \
            self.rules == other.rules and \
            self.verbosity == other.verbosity and \
            self.target == other.target and \
            self.extra_path == other.extra_path and \
            self.contrib == other.contrib and \
            self.ignore_merge_commits == other.ignore_merge_commits and \
            self.ignore_fixup_commits == other.ignore_fixup_commits and \
            self.ignore_squash_commits == other.ignore_squash_commits and \
            self.ignore_revert_commits == other.ignore_revert_commits and \
            self.ignore_stdin == other.ignore_stdin and \
            self.staged == other.staged and \
            self.debug == other.debug and \
            self.ignore == other.ignore and \
            self._config_path == other._config_path  # noqa

    def __ne__(self, other):
        return not self.__eq__(other)  # required for py2

    def __str__(self):
        # config-path is not a user exposed variable, so don't print it under the general section
        return_str = u"config-path: {0}\n".format(self._config_path)
        return_str += u"[GENERAL]\n"
        return_str += u"extra-path: {0}\n".format(self.extra_path)
        return_str += u"contrib: {0}\n".format(self.contrib)
        return_str += u"ignore: {0}\n".format(",".join(self.ignore))
        return_str += u"ignore-merge-commits: {0}\n".format(self.ignore_merge_commits)
        return_str += u"ignore-fixup-commits: {0}\n".format(self.ignore_fixup_commits)
        return_str += u"ignore-squash-commits: {0}\n".format(self.ignore_squash_commits)
        return_str += u"ignore-revert-commits: {0}\n".format(self.ignore_revert_commits)
        return_str += u"ignore-stdin: {0}\n".format(self.ignore_stdin)
        return_str += u"staged: {0}\n".format(self.staged)
        return_str += u"verbosity: {0}\n".format(self.verbosity)
        return_str += u"debug: {0}\n".format(self.debug)
        return_str += u"target: {0}\n".format(self.target)
        return_str += u"[RULES]\n{0}".format(self.rules)
        return return_str


class RuleCollection(object):
    """ Class representing an ordered list of rules. Methods are provided to easily retrieve, add or delete rules. """

    def __init__(self, rule_classes=None, rule_attrs=None):
        # Use an ordered dict so that the order in which rules are applied is always the same
        self._rules = OrderedDict()
        if rule_classes:
            self.add_rules(rule_classes, rule_attrs)

    def find_rule(self, rule_id_or_name):
        # try finding rule by id
        rule_id_or_name = ustr(rule_id_or_name)  # convert to unicode first
        rule = self._rules.get(rule_id_or_name)
        # if not found, try finding rule by name
        if not rule:
            rule = next((rule for rule in self._rules.values() if rule.name == rule_id_or_name), None)
        return rule

    def add_rule(self, rule_class, rule_id, rule_attrs=None):
        """ Instantiates and adds a rule to RuleCollection.
            Note: There can be multiple instantiations of the same rule_class in the RuleCollection, as long as the
            rule_id is unique.
            :param rule_class python class representing the rule
            :param rule_id unique identifier for the rule. If not unique, it will
                           overwrite the existing rule with that id
            :param rule_attrs dictionary of attributes to set on the instantiated rule obj
        """
        rule_obj = rule_class()
        rule_obj.id = rule_id
        if rule_attrs:
            for key, val in rule_attrs.items():
                setattr(rule_obj, key, val)
        self._rules[rule_obj.id] = rule_obj

    def add_rules(self, rule_classes, rule_attrs=None):
        """ Convenience method to add multiple rules at once based on a list of rule classes. """
        for rule_class in rule_classes:
            self.add_rule(rule_class, rule_class.id, rule_attrs)

    def delete_rules_by_attr(self, attr_name, attr_val):
        """ Deletes all rules from the collection that match a given attribute name and value """
        # Create a new list based on _rules.values() because in python 3, values() is a ValuesView as opposed to a list
        # This means you can't modify the ValueView while iterating over it.
        for rule in [r for r in self._rules.values()]:
            if hasattr(rule, attr_name) and (getattr(rule, attr_name) == attr_val):
                del self._rules[rule.id]

    def __iter__(self):
        for rule in self._rules.values():
            yield rule

    def __eq__(self, other):
        return isinstance(other, RuleCollection) and self._rules == other._rules

    def __ne__(self, other):
        return not self.__eq__(other)  # required for py2

    def __len__(self):
        return len(self._rules)

    def __str__(self):
        return_str = ""
        for rule in self._rules.values():
            return_str += u"  {0}: {1}\n".format(rule.id, rule.name)
            for option_name, option_value in sorted(rule.options.items()):
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
        for line in commit.message.body:
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
        self._config_path = os.path.realpath(filename)
        try:
            parser = ConfigParser()

            with io.open(filename, encoding=DEFAULT_ENCODING) as config_file:
                # readfp() is deprecated in python 3.2+, but compatible with 2.7
                parser.readfp(config_file, filename)  # pylint: disable=deprecated-method

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

    def clone(self):
        """ Creates an exact copy of a LintConfigBuilder.  """
        builder = LintConfigBuilder()
        builder._config_blueprint = copy.deepcopy(self._config_blueprint)
        builder._config_path = self._config_path
        return builder


GITLINT_CONFIG_TEMPLATE_SRC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files/gitlint")


class LintConfigGenerator(object):
    @staticmethod
    def generate_config(dest):
        """ Generates a gitlint config file at the given destination location.
            Expects that the given ```dest``` points to a valid destination. """
        shutil.copyfile(GITLINT_CONFIG_TEMPLATE_SRC_PATH, dest)
