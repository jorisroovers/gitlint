import copy
import os
import re
import shutil
from collections import OrderedDict
from configparser import ConfigParser
from configparser import Error as ConfigParserError
from dataclasses import dataclass, field
from typing import ClassVar, Optional

from gitlint import (
    options,
    rule_finder,
    rules,
)
from gitlint.contrib import rules as contrib_rules
from gitlint.exception import GitlintError
from gitlint.utils import FILE_ENCODING


def handle_option_error(func):
    """Decorator that calls given method/function and handles any RuleOptionError gracefully by converting it to a
    LintConfigError."""

    def wrapped(*args):
        try:
            return func(*args)
        except options.RuleOptionError as e:
            raise LintConfigError(str(e)) from e

    return wrapped


class LintConfigError(GitlintError):
    pass


class LintConfig:
    """Class representing gitlint configuration.
    Contains active config as well as number of methods to easily get/set the config.
    """

    # Default tuple of rule classes (tuple because immutable).
    default_rule_classes = (
        rules.IgnoreByTitle,
        rules.IgnoreByBody,
        rules.IgnoreBodyLines,
        rules.IgnoreByAuthorName,
        rules.TitleMaxLength,
        rules.TitleTrailingWhitespace,
        rules.TitleLeadingWhitespace,
        rules.TitleTrailingPunctuation,
        rules.TitleHardTab,
        rules.TitleMustNotContainWord,
        rules.TitleRegexMatches,
        rules.TitleMinLength,
        rules.BodyMaxLineLength,
        rules.BodyMinLength,
        rules.BodyMissing,
        rules.BodyTrailingWhitespace,
        rules.BodyHardTab,
        rules.BodyFirstLineEmpty,
        rules.BodyChangedFileMention,
        rules.BodyRegexMatches,
        rules.AuthorValidEmail,
    )

    def __init__(self):
        self.rules = RuleCollection(self.default_rule_classes)
        self._verbosity = options.IntOption("verbosity", 3, "Verbosity")
        self._ignore_merge_commits = options.BoolOption("ignore-merge-commits", True, "Ignore merge commits")
        self._ignore_fixup_commits = options.BoolOption("ignore-fixup-commits", True, "Ignore fixup commits")
        self._ignore_fixup_amend_commits = options.BoolOption(
            "ignore-fixup-amend-commits", True, "Ignore fixup amend commits"
        )
        self._ignore_squash_commits = options.BoolOption("ignore-squash-commits", True, "Ignore squash commits")
        self._ignore_revert_commits = options.BoolOption("ignore-revert-commits", True, "Ignore revert commits")
        self._debug = options.BoolOption("debug", False, "Enable debug mode")
        self._extra_path = None
        target_description = "Path of the target git repository (default=current working directory)"
        self._target = options.PathOption("target", os.path.realpath(os.getcwd()), target_description)
        self._ignore = options.ListOption("ignore", [], "List of rule-ids to ignore")
        self._contrib = options.ListOption("contrib", [], "List of contrib-rules to enable")
        self._config_path = None
        ignore_stdin_description = "Ignore any stdin data. Useful for running in CI server."
        self._ignore_stdin = options.BoolOption("ignore-stdin", False, ignore_stdin_description)
        self._staged = options.BoolOption("staged", False, "Read staged commit meta-info from the local repository.")
        self._fail_without_commits = options.BoolOption(
            "fail-without-commits", False, "Hard fail when the target commit range is empty"
        )
        self._regex_style_search = options.BoolOption(
            "regex-style-search", False, "Use `search` instead of `match` semantics for regex rules"
        )

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
        if self.verbosity < 0 or self.verbosity > 3:  # noqa: PLR2004 (Magic value used in comparison)
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
    def ignore_fixup_amend_commits(self):
        return self._ignore_fixup_amend_commits.value

    @ignore_fixup_amend_commits.setter
    @handle_option_error
    def ignore_fixup_amend_commits(self, value):
        return self._ignore_fixup_amend_commits.set(value)

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
    def fail_without_commits(self):
        return self._fail_without_commits.value

    @fail_without_commits.setter
    @handle_option_error
    def fail_without_commits(self, value):
        return self._fail_without_commits.set(value)

    @property
    def regex_style_search(self):
        return self._regex_style_search.value

    @regex_style_search.setter
    @handle_option_error
    def regex_style_search(self, value):
        return self._regex_style_search.set(value)

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
                    "extra-path", value, "Path to a directory or module with extra user-defined rules", type="both"
                )

            # Make sure we unload any previously loaded extra-path rules
            self.rules.delete_rules_by_attr("is_user_defined", True)

            # Find rules in the new extra-path and add them to the existing rules
            rule_classes = rule_finder.find_rule_classes(self.extra_path)
            self.rules.add_rules(rule_classes, {"is_user_defined": True})

        except (options.RuleOptionError, rules.UserRuleError) as e:
            raise LintConfigError(str(e)) from e

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
                rule_class = next((rc for rc in rule_classes if rule_id_or_name in (rc.id, rc.name)), False)

                # If contrib rule exists, instantiate it and add it to the rules list
                if rule_class:
                    self.rules.add_rule(rule_class, rule_class.id, {"is_contrib": True})
                else:
                    raise LintConfigError(f"No contrib rule with id or name '{rule_id_or_name}' found.")

        except (options.RuleOptionError, rules.UserRuleError) as e:
            raise LintConfigError(str(e)) from e

    def _get_option(self, rule_name_or_id, option_name):
        rule = self.rules.find_rule(rule_name_or_id)
        if not rule:
            raise LintConfigError(f"No such rule '{rule_name_or_id}'")

        option = rule.options.get(option_name)
        if not option:
            raise LintConfigError(f"Rule '{rule_name_or_id}' has no option '{option_name}'")

        return option

    def get_rule_option(self, rule_name_or_id, option_name):
        """Returns the value of a given option for a given rule. LintConfigErrors will be raised if the
        rule or option don't exist."""
        option = self._get_option(rule_name_or_id, option_name)
        return option.value

    def set_rule_option(self, rule_name_or_id, option_name, option_value):
        """Attempts to set a given value for a given option for a given rule.
        LintConfigErrors will be raised if the rule or option don't exist or if the value is invalid."""
        option = self._get_option(rule_name_or_id, option_name)
        try:
            option.set(option_value)
        except options.RuleOptionError as e:
            msg = f"'{option_value}' is not a valid value for option '{rule_name_or_id}.{option_name}'. {e}."
            raise LintConfigError(msg) from e

    def set_general_option(self, option_name, option_value):
        attr_name = option_name.replace("-", "_")
        # only allow setting general options that exist and don't start with an underscore
        if not hasattr(self, attr_name) or attr_name[0] == "_":
            raise LintConfigError(f"'{option_name}' is not a valid gitlint option")

        # else
        setattr(self, attr_name, option_value)

    def __eq__(self, other):
        return (
            isinstance(other, LintConfig)
            and self.rules == other.rules
            and self.verbosity == other.verbosity
            and self.target == other.target
            and self.extra_path == other.extra_path
            and self.contrib == other.contrib
            and self.ignore_merge_commits == other.ignore_merge_commits
            and self.ignore_fixup_commits == other.ignore_fixup_commits
            and self.ignore_fixup_amend_commits == other.ignore_fixup_amend_commits
            and self.ignore_squash_commits == other.ignore_squash_commits
            and self.ignore_revert_commits == other.ignore_revert_commits
            and self.ignore_stdin == other.ignore_stdin
            and self.staged == other.staged
            and self.fail_without_commits == other.fail_without_commits
            and self.regex_style_search == other.regex_style_search
            and self.debug == other.debug
            and self.ignore == other.ignore
            and self._config_path == other._config_path
        )

    def __str__(self):
        # config-path is not a user exposed variable, so don't print it under the general section
        return (
            f"config-path: {self._config_path}\n"
            "[GENERAL]\n"
            f"extra-path: {self.extra_path}\n"
            f"contrib: {self.contrib}\n"
            f"ignore: {','.join(self.ignore)}\n"
            f"ignore-merge-commits: {self.ignore_merge_commits}\n"
            f"ignore-fixup-commits: {self.ignore_fixup_commits}\n"
            f"ignore-fixup-amend-commits: {self.ignore_fixup_amend_commits}\n"
            f"ignore-squash-commits: {self.ignore_squash_commits}\n"
            f"ignore-revert-commits: {self.ignore_revert_commits}\n"
            f"ignore-stdin: {self.ignore_stdin}\n"
            f"staged: {self.staged}\n"
            f"fail-without-commits: {self.fail_without_commits}\n"
            f"regex-style-search: {self.regex_style_search}\n"
            f"verbosity: {self.verbosity}\n"
            f"debug: {self.debug}\n"
            f"target: {self.target}\n"
            f"[RULES]\n{self.rules}"
        )


class RuleCollection:
    """Class representing an ordered list of rules. Methods are provided to easily retrieve, add or delete rules."""

    def __init__(self, rule_classes=None, rule_attrs=None):
        # Use an ordered dict so that the order in which rules are applied is always the same
        self._rules = OrderedDict()
        if rule_classes:
            self.add_rules(rule_classes, rule_attrs)

    def find_rule(self, rule_id_or_name):
        rule = self._rules.get(rule_id_or_name)
        # if not found, try finding rule by name
        if not rule:
            rule = next((rule for rule in self._rules.values() if rule.name == rule_id_or_name), None)
        return rule

    def add_rule(self, rule_class, rule_id, rule_attrs=None):
        """Instantiates and adds a rule to RuleCollection.
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
        """Convenience method to add multiple rules at once based on a list of rule classes."""
        for rule_class in rule_classes:
            self.add_rule(rule_class, rule_class.id, rule_attrs)

    def delete_rules_by_attr(self, attr_name, attr_val):
        """Deletes all rules from the collection that match a given attribute name and value"""
        # Create a new list based on _rules.values() because in python 3, values() is a ValuesView as opposed to a list
        # This means you can't modify the ValueView while iterating over it.
        for rule in list(self._rules.values()):
            if hasattr(rule, attr_name) and (getattr(rule, attr_name) == attr_val):
                del self._rules[rule.id]

    def __iter__(self):
        yield from self._rules.values()

    def __eq__(self, other):
        return isinstance(other, RuleCollection) and self._rules == other._rules

    def __len__(self):
        return len(self._rules)

    def __str__(self):
        return_str = ""
        for rule in self._rules.values():
            return_str += f"  {rule.id}: {rule.name}\n"
            for option_name, option_value in sorted(rule.options.items()):
                if option_value.value is None:
                    option_val_repr = None
                elif isinstance(option_value.value, list):
                    option_val_repr = ",".join(option_value.value)
                elif isinstance(option_value, options.RegexOption):
                    option_val_repr = option_value.value.pattern
                else:
                    option_val_repr = option_value.value
                return_str += f"     {option_name}={option_val_repr}\n"
        return return_str


@dataclass
class LintConfigBuilder:
    """Factory class that can build gitlint config.
    This is primarily useful to deal with complex configuration scenarios where configuration can be set and overridden
    from various sources (typically according to certain precedence rules) before the actual config should be
    normalized, validated and build. Example usage can be found in gitlint.cli.
    """

    RULE_QUALIFIER_SYMBOL: ClassVar[str] = ":"
    _config_blueprint: OrderedDict = field(init=False, default_factory=OrderedDict)
    _config_path: Optional[str] = field(init=False, default=None)

    def set_option(self, section, option_name, option_value):
        if section not in self._config_blueprint:
            self._config_blueprint[section] = OrderedDict()
        self._config_blueprint[section][option_name] = option_value

    def set_config_from_commit(self, commit):
        """Given a git commit, applies config specified in the commit message.
        Supported:
         - gitlint-ignore: all
        """
        for line in commit.message.body:
            pattern = re.compile(r"^gitlint-ignore:\s*(.*)")
            matches = pattern.match(line)
            if matches and len(matches.groups()) == 1:
                self.set_option("general", "ignore", matches.group(1))

    def set_config_from_string_list(self, config_options):
        """Given a list of config options of the form "<rule>.<option>=<value>", parses out the correct rule and option
        and sets the value accordingly in this factory object."""
        for config_option in config_options:
            try:
                config_name, option_value = config_option.split("=", 1)
                if not option_value:
                    raise ValueError()
                rule_name, option_name = config_name.split(".", 1)
                self.set_option(rule_name, option_name, option_value)
            except ValueError as e:  # raised if the config string is invalid
                raise LintConfigError(
                    f"'{config_option}' is an invalid configuration option. Use '<rule>.<option>=<value>'"
                ) from e

    def set_from_config_file(self, filename):
        """Loads lint config from an ini-style config file"""
        if not os.path.exists(filename):
            raise LintConfigError(f"Invalid file path: {filename}")
        self._config_path = os.path.realpath(filename)
        try:
            parser = ConfigParser()

            with open(filename, encoding=FILE_ENCODING) as config_file:
                parser.read_file(config_file, filename)

            for section_name in parser.sections():
                for option_name, option_value in parser.items(section_name):
                    self.set_option(section_name, option_name, str(option_value))

        except ConfigParserError as e:
            raise LintConfigError(str(e)) from e

    def _add_named_rule(self, config, qualified_rule_name):
        """Adds a Named Rule to a given LintConfig object.
        IMPORTANT: This method does *NOT* overwrite existing Named Rules with the same canonical id.
        """

        # Split up named rule in its parts: the name/id that specifies the parent rule,
        # And the name of the rule instance itself
        rule_name_parts = qualified_rule_name.split(self.RULE_QUALIFIER_SYMBOL, 1)
        rule_name = rule_name_parts[1].strip()
        parent_rule_specifier = rule_name_parts[0].strip()

        # assert that the rule name is valid:
        # - not empty
        # - no whitespace or colons
        if rule_name == "" or bool(re.search("\\s|:", rule_name, re.UNICODE)):
            msg = f"The rule-name part in '{qualified_rule_name}' cannot contain whitespace, colons or be empty"
            raise LintConfigError(msg)

        # find parent rule
        parent_rule = config.rules.find_rule(parent_rule_specifier)
        if not parent_rule:
            msg = f"No such rule '{parent_rule_specifier}' (named rule: '{qualified_rule_name}')"
            raise LintConfigError(msg)

        # Determine canonical id and name by recombining the parent id/name and instance name parts.
        canonical_id = parent_rule.__class__.id + self.RULE_QUALIFIER_SYMBOL + rule_name
        canonical_name = parent_rule.__class__.name + self.RULE_QUALIFIER_SYMBOL + rule_name

        # Add the rule to the collection of rules if it's not there already
        if not config.rules.find_rule(canonical_id):
            config.rules.add_rule(parent_rule.__class__, canonical_id, {"is_named": True, "name": canonical_name})

        return canonical_id

    def build(self, config=None):
        """Build a real LintConfig object by normalizing and validating the options that were previously set on this
        factory."""
        # If we are passed a config object, then rebuild that object instead of building a new lintconfig object from
        # scratch
        if not config:
            config = LintConfig()

        config._config_path = self._config_path

        # Set general options first as this might change the behavior or validity of the other options
        general_section = self._config_blueprint.get("general")
        if general_section:
            for option_name, option_value in general_section.items():
                config.set_general_option(option_name, option_value)

        for section_name, section_dict in self._config_blueprint.items():
            for option_name, option_value in section_dict.items():
                qualified_section_name = section_name
                # Skip over the general section, as we've already done that above
                if qualified_section_name != "general":
                    # If the section name contains a colon (:), then this section is defining a Named Rule
                    # Which means we need to instantiate that Named Rule in the config.
                    if self.RULE_QUALIFIER_SYMBOL in section_name:
                        qualified_section_name = self._add_named_rule(config, qualified_section_name)

                    config.set_rule_option(qualified_section_name, option_name, option_value)

        return config

    def clone(self):
        """Creates an exact copy of a LintConfigBuilder."""
        builder = LintConfigBuilder()
        builder._config_blueprint = copy.deepcopy(self._config_blueprint)
        builder._config_path = self._config_path
        return builder


GITLINT_CONFIG_TEMPLATE_SRC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files/gitlint")


class LintConfigGenerator:
    @staticmethod
    def generate_config(dest):
        """Generates a gitlint config file at the given destination location.
        Expects that the given ```dest``` points to a valid destination."""
        shutil.copyfile(GITLINT_CONFIG_TEMPLATE_SRC_PATH, dest)
