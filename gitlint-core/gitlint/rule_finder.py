import fnmatch
import importlib
import inspect
import os
import sys

from gitlint import options, rules


def find_rule_classes(extra_path):
    """
    Searches a given directory or python module for rule classes. This is done by
    adding the directory path to the python path, importing the modules and then finding
    any Rule class in those modules.

    :param extra_path: absolute directory or file path to search for rule classes
    :return: The list of rule classes that are found in the given directory or module
    """

    files = []
    modules = []

    if os.path.isfile(extra_path):
        files = [os.path.basename(extra_path)]
        directory = os.path.dirname(extra_path)
    elif os.path.isdir(extra_path):
        files = os.listdir(extra_path)
        directory = extra_path
    else:
        raise rules.UserRuleError(f"Invalid extra-path: {extra_path}")

    # Filter out files that are not python modules
    for filename in files:
        if fnmatch.fnmatch(filename, "*.py"):
            # We have to treat __init__ files a bit special: add the parent dir instead of the filename, and also
            # add their parent dir to the sys.path (this fixes import issues with pypy2).
            if filename == "__init__.py":
                modules.append(os.path.basename(directory))
                sys.path.append(os.path.dirname(directory))
            else:
                modules.append(os.path.splitext(filename)[0])

    # No need to continue if there are no modules specified
    if not modules:
        return []

    # Append the extra rules path to python path so that we can import them
    sys.path.append(directory)

    # Find all the rule classes in the found python files
    rule_classes = []
    for module in modules:
        # Import the module
        try:
            importlib.import_module(module)

        except Exception as e:
            raise rules.UserRuleError(f"Error while importing extra-path module '{module}': {e}") from e

        # Find all rule classes in the module. We do this my inspecting all members of the module and checking
        # 1) is it a class, if not, skip
        # 2) is the parent path the current module. If not, we are dealing with an imported class, skip
        # 3) is it a subclass of rule
        rule_classes.extend(
            [
                clazz
                for _, clazz in inspect.getmembers(sys.modules[module])
                if inspect.isclass(clazz)  # check isclass to ensure clazz.__module__ exists
                and clazz.__module__ == module  # ignore imported classes
                and (issubclass(clazz, (rules.LineRule, rules.CommitRule, rules.ConfigurationRule)))
            ]
        )

        # validate that the rule classes are valid user-defined rules
        for rule_class in rule_classes:
            assert_valid_rule_class(rule_class)

    return rule_classes


def assert_valid_rule_class(clazz, rule_type="User-defined"):  # noqa: PLR0912 (too many branches)
    """
    Asserts that a given rule clazz is valid by checking a number of its properties:
     - Rules must extend from  LineRule, CommitRule or ConfigurationRule
     - Rule classes must have id and name string attributes.
       The options_spec is optional, but if set, it must be a list of gitlint Options.
     - Rule classes must have a validate method. In case of a CommitRule, validate must take a single commit parameter.
       In case of LineRule, validate must take line and commit as first and second parameters.
     - LineRule classes must have a target class attributes that is set to either
    - ConfigurationRule classes must have an apply method that take `config` and `commit` as parameters.
       CommitMessageTitle or CommitMessageBody.
     - Rule id's cannot start with R, T, B, M or I as these rule ids are reserved for gitlint itself.
    """

    # Rules must extend from LineRule, CommitRule or ConfigurationRule
    if not issubclass(clazz, (rules.LineRule, rules.CommitRule, rules.ConfigurationRule)):
        msg = (
            f"{rule_type} rule class '{clazz.__name__}' "
            f"must extend from {rules.CommitRule.__module__}.{rules.LineRule.__name__}, "
            f"{rules.CommitRule.__module__}.{rules.CommitRule.__name__} or "
            f"{rules.CommitRule.__module__}.{rules.ConfigurationRule.__name__}"
        )
        raise rules.UserRuleError(msg)

    # Rules must have an id attribute
    if not hasattr(clazz, "id") or clazz.id is None or not clazz.id:
        raise rules.UserRuleError(f"{rule_type} rule class '{clazz.__name__}' must have an 'id' attribute")

    # Rule id's cannot start with gitlint reserved letters
    if clazz.id[0].upper() in ["R", "T", "B", "M", "I"]:
        msg = f"The id '{clazz.id[0]}' of '{clazz.__name__}' is invalid. Gitlint reserves ids starting with R,T,B,M,I"
        raise rules.UserRuleError(msg)

    # Rules must have a name attribute
    if not hasattr(clazz, "name") or clazz.name is None or not clazz.name:
        raise rules.UserRuleError(f"{rule_type} rule class '{clazz.__name__}' must have a 'name' attribute")

    # if set, options_spec must be a list of RuleOption
    if not isinstance(clazz.options_spec, list):
        msg = (
            f"The options_spec attribute of {rule_type.lower()} rule class '{clazz.__name__}' "
            f"must be a list of {options.RuleOption.__module__}.{options.RuleOption.__name__}"
        )
        raise rules.UserRuleError(msg)

    # check that all items in options_spec are actual gitlint options
    for option in clazz.options_spec:
        if not isinstance(option, options.RuleOption):
            msg = (
                f"The options_spec attribute of {rule_type.lower()} rule class '{clazz.__name__}' "
                f"must be a list of {options.RuleOption.__module__}.{options.RuleOption.__name__}"
            )
            raise rules.UserRuleError(msg)

    # Line/Commit rules must have a `validate` method
    # We use isroutine() as it's both python 2 and 3 compatible. Details: http://stackoverflow.com/a/17019998/381010
    if issubclass(clazz, (rules.LineRule, rules.CommitRule)):
        if not hasattr(clazz, "validate") or not inspect.isroutine(clazz.validate):
            raise rules.UserRuleError(f"{rule_type} rule class '{clazz.__name__}' must have a 'validate' method")

    # Configuration rules must have an `apply` method
    elif issubclass(clazz, rules.ConfigurationRule):  # noqa: SIM102
        if not hasattr(clazz, "apply") or not inspect.isroutine(clazz.apply):
            msg = f"{rule_type} Configuration rule class '{clazz.__name__}' must have an 'apply' method"
            raise rules.UserRuleError(msg)

    # LineRules must have a valid target: rules.CommitMessageTitle or rules.CommitMessageBody
    if issubclass(clazz, rules.LineRule):  # noqa: SIM102
        if clazz.target not in [rules.CommitMessageTitle, rules.CommitMessageBody]:
            msg = (
                f"The target attribute of the {rule_type.lower()} LineRule class '{clazz.__name__}' "
                f"must be either {rules.CommitMessageTitle.__module__}.{rules.CommitMessageTitle.__name__} "
                f"or {rules.CommitMessageTitle.__module__}.{rules.CommitMessageBody.__name__}"
            )
            raise rules.UserRuleError(msg)
