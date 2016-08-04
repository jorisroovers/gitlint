import fnmatch
import inspect
import importlib
import os
import sys

from gitlint import rules


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
        importlib.import_module(module)

        # Find all rule classes in the module. We do this my inspecting all members of the module and checking
        # 1) is it a class, if not, skip
        # 2) is the parent path the current module. If not, we are dealing with an imported class, skip
        # 3) is it a subclass of rule
        rule_classes.extend([clazz for _, clazz in inspect.getmembers(sys.modules[module])
                             if
                             inspect.isclass(clazz) and
                             clazz.__module__ == module and
                             issubclass(clazz, rules.Rule) and
                             assert_valid_rule_class(clazz)])

    return rule_classes


def assert_valid_rule_class(_clazz):
    # TODO (joris.roovers): checks whether the rule class is valid
    # e.g.: it has an id and name and are of type string, default constructor, etc
    return True
