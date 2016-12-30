import fnmatch
import inspect
import os
import sys
import importlib

from gitlint import rules, options
from gitlint.utils import ustr


class UserRuleError(Exception):
    """ Error used to indicate that an error occurred while trying to load a user rule """
    pass


def find_rule_classes(extra_path):
    """
    Searches a given directory for rule classes. This is done by finding all python modules in the given directory,
    adding them to the python path, importing them and then finding any Rule classes in those modules.

    :param extra_path: absolute directory path to search for rule classes
    :return: The list of rule classes that are found in the given directory.
    """

    # Find all python files in the given path
    modules = []
    for filename in os.listdir(extra_path):
        if fnmatch.fnmatch(filename, '*.py'):
            modules.append(os.path.splitext(filename)[0])

    # No need to continue if there are no modules specified
    if len(modules) == 0:
        return []

    # Append the extra_path to the python path so that we can import the newly found rule modules
    sys.path.append(extra_path)

    # Find all the rule classes in the found python files
    rule_classes = []
    for module in modules:
        # Import the module
        try:
            importlib.import_module(module)
        except Exception as e:
            raise UserRuleError(u"Error while importing extra-path module '{0}': {1}".format(module, ustr(e)))

        # Find all rule classes in the module. We do this my inspecting all members of the module and checking
        # 1) is it a class, if not, skip
        # 2) is the parent path the current module. If not, we are dealing with an imported class, skip
        # 3) is it a subclass of rule
        rule_classes.extend([clazz for _, clazz in inspect.getmembers(sys.modules[module])
                             if
                             inspect.isclass(clazz) and  # check isclass to ensure clazz.__module__ exists
                             clazz.__module__ == module and  # ignore imported classes
                             (issubclass(clazz, rules.LineRule) or issubclass(clazz, rules.CommitRule))])

        # validate that the rule classes are valid user-defined rules
        for rule_class in rule_classes:
            assert_valid_rule_class(rule_class)

    return rule_classes


def assert_valid_rule_class(clazz):
    """
    Asserts that a given rule clazz is valid by checking a number of its properties:
     - Rules must extend from  LineRule or CommitRule
     - Rule classes must have id and name string attributes.
       The options_spec is optional, but if set, it must be a list of gitlint Options.
     - Rule classes must have a validate method. In case of a CommitRule, validate must take a single commit parameter.
       In case of LineRule, validate must take line and commit as first and second parameters.
     - LineRule classes must have a target class attributes that is set to either
       CommitMessageTitle or CommitMessageBody.
     - User Rule id's cannot start with R, T, B or M as these rule ids are reserved for gitlint itself.
    """

    # Rules must extend from LineRule or CommitRule
    if not (issubclass(clazz, rules.LineRule) or issubclass(clazz, rules.CommitRule)):
        msg = u"User-defined rule class '{0}' must extend from {1}.{2} or {1}.{3}"
        raise UserRuleError(msg.format(clazz.__name__, rules.CommitRule.__module__,
                                       rules.LineRule.__name__, rules.CommitRule.__name__))

    # Rules must have an id attribute
    if not hasattr(clazz, 'id') or clazz.id is None or len(clazz.id) == 0:
        raise UserRuleError(u"User-defined rule class '{0}' must have an 'id' attribute".format(clazz.__name__))

    # Rule id's cannot start with gitlint reserved letters
    if clazz.id[0].upper() in ['R', 'T', 'B', 'M']:
        msg = u"The id '{1}' of '{0}' is invalid. Gitlint reserves ids starting with R,T,B,M"
        raise UserRuleError(msg.format(clazz.__name__, clazz.id[0]))

    # Rules must have a name attribute
    if not hasattr(clazz, 'name') or clazz.name is None or len(clazz.name) == 0:
        raise UserRuleError(u"User-defined rule class '{0}' must have a 'name' attribute".format(clazz.__name__))

    # if set, options_spec must be a list of RuleOption
    if not isinstance(clazz.options_spec, list):
        msg = u"The options_spec attribute of user-defined rule class '{0}' must be a list of {1}.{2}"
        raise UserRuleError(msg.format(clazz.__name__, options.RuleOption.__module__, options.RuleOption.__name__))

    # check that all items in options_spec are actual gitlint options
    for option in clazz.options_spec:
        if not isinstance(option, options.RuleOption):
            msg = u"The options_spec attribute of user-defined rule class '{0}' must be a list of {1}.{2}"
            raise UserRuleError(msg.format(clazz.__name__, options.RuleOption.__module__, options.RuleOption.__name__))

    # Rules must have a validate method. We use isroutine() as it's both python 2 and 3 compatible.
    # For more info see http://stackoverflow.com/a/17019998/381010
    if not hasattr(clazz, 'validate') or not inspect.isroutine(clazz.validate):
        raise UserRuleError(u"User-defined rule class '{0}' must have a 'validate' method".format(clazz.__name__))

    # LineRules must have a valid target: rules.CommitMessageTitle or rules.CommitMessageBody
    if issubclass(clazz, rules.LineRule):
        if clazz.target not in [rules.CommitMessageTitle, rules.CommitMessageBody]:
            msg = u"The target attribute of the user-defined LineRule class '{0}' must be either {1}.{2} or {1}.{3}"
            msg = msg.format(clazz.__name__, rules.CommitMessageTitle.__module__,
                             rules.CommitMessageTitle.__name__, rules.CommitMessageBody.__name__)
            raise UserRuleError(msg)
