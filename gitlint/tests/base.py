# -*- coding: utf-8 -*-

import contextlib
import copy
import io
import logging
import os
import re
import shutil
import tempfile

try:
    # python 2.x
    import unittest2 as unittest
except ImportError:
    # python 3.x
    import unittest

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.git import GitContext
from gitlint.utils import ustr, IS_PY2, LOG_FORMAT, DEFAULT_ENCODING


# unittest2's assertRaisesRegex doesn't do unicode comparison.
# Let's monkeypatch the str() function to point to unicode() so that it does :)
# For reference, this is where this patch is required:
# https://hg.python.org/unittest2/file/tip/unittest2/case.py#l227
try:
    # python 2.x
    unittest.case.str = unicode
except (AttributeError, NameError):
    pass  # python 3.x


class BaseTestCase(unittest.TestCase):
    """ Base class of which all gitlint unit test classes are derived. Provides a number of convenience methods. """

    # In case of assert failures, print the full error message
    maxDiff = None

    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
    EXPECTED_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
    GITLINT_USE_SH_LIB = os.environ.get("GITLINT_USE_SH_LIB", "[NOT SET]")

    def setUp(self):
        self.logcapture = LogCapture()
        self.logcapture.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger('gitlint').setLevel(logging.DEBUG)
        logging.getLogger('gitlint').handlers = [self.logcapture]

        # Make sure we don't propagate anything to child loggers, we need to do this explicitely here
        # because if you run a specific test file like test_lint.py, we won't be calling the setupLogging() method
        # in gitlint.cli that normally takes care of this
        logging.getLogger('gitlint').propagate = False

    @staticmethod
    @contextlib.contextmanager
    def tempdir():
        tmpdir = tempfile.mkdtemp()
        try:
            yield tmpdir
        finally:
            shutil.rmtree(tmpdir)

    @staticmethod
    def get_sample_path(filename=""):
        # Don't join up empty files names because this will add a trailing slash
        if filename == "":
            return ustr(BaseTestCase.SAMPLES_DIR)

        return ustr(os.path.join(BaseTestCase.SAMPLES_DIR, filename))

    @staticmethod
    def get_sample(filename=""):
        """ Read and return the contents of a file in gitlint/tests/samples """
        sample_path = BaseTestCase.get_sample_path(filename)
        with io.open(sample_path, encoding=DEFAULT_ENCODING) as content:
            sample = ustr(content.read())
        return sample

    @staticmethod
    def patch_input(side_effect):
        """ Patches the built-in input() with a provided side-effect """
        module_path = "builtins.input"
        if IS_PY2:
            module_path = "__builtin__.raw_input"
        patched_module = patch(module_path, side_effect=side_effect)
        return patched_module

    @staticmethod
    def get_expected(filename="", variable_dict=None):
        """ Utility method to read an expected file from gitlint/tests/expected and return it as a string.
        Optionally replace template variables specified by variable_dict. """
        expected_path = os.path.join(BaseTestCase.EXPECTED_DIR, filename)
        with io.open(expected_path, encoding=DEFAULT_ENCODING) as content:
            expected = ustr(content.read())

        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected

    @staticmethod
    def get_user_rules_path():
        return os.path.join(BaseTestCase.SAMPLES_DIR, "user_rules")

    @staticmethod
    def gitcontext(commit_msg_str, changed_files=None, ):
        """ Utility method to easily create gitcontext objects based on a given commit msg string and an optional set of
        changed files"""
        with patch("gitlint.git.git_commentchar") as comment_char:
            comment_char.return_value = u"#"
            gitcontext = GitContext.from_commit_msg(commit_msg_str)
            commit = gitcontext.commits[-1]
            if changed_files:
                commit.changed_files = changed_files
            return gitcontext

    @staticmethod
    def gitcommit(commit_msg_str, changed_files=None, **kwargs):
        """ Utility method to easily create git commit given a commit msg string and an optional set of changed files"""
        gitcontext = BaseTestCase.gitcontext(commit_msg_str, changed_files)
        commit = gitcontext.commits[-1]
        for attr, value in kwargs.items():
            setattr(commit, attr, value)
        return commit

    def assert_logged(self, expected):
        """ Asserts that the logs match an expected string or list.
            This method knows how to compare a passed list of log lines as well as a newline concatenated string
            of all loglines. """
        if isinstance(expected, list):
            self.assertListEqual(self.logcapture.messages, expected)
        else:
            self.assertEqual("\n".join(self.logcapture.messages), expected)

    def assert_log_contains(self, line):
        """ Asserts that a certain line is in the logs """
        self.assertIn(line, self.logcapture.messages)

    def assertRaisesRegex(self, expected_exception, expected_regex, *args, **kwargs):
        """ Pass-through method to unittest.TestCase.assertRaisesRegex that applies re.escape() to the passed
            `expected_regex`. This is useful to automatically escape all file paths that might be present in the regex.
        """
        return super(BaseTestCase, self).assertRaisesRegex(expected_exception, re.escape(expected_regex),
                                                           *args, **kwargs)

    @contextlib.contextmanager
    def assertRaisesMessage(self, expected_exception, expected_msg):  # pylint: disable=invalid-name
        """ Asserts an exception has occurred with a given error message """
        try:
            yield
        except expected_exception as exc:
            exception_msg = ustr(exc)
            if exception_msg != expected_msg:
                error = u"Right exception, wrong message:\n      got: {0}\n expected: {1}"
                raise self.fail(error.format(exception_msg, expected_msg))
            # else: everything is fine, just return
            return
        except Exception as exc:
            raise self.fail(u"Expected '{0}' got '{1}'".format(expected_exception.__name__, exc.__class__.__name__))

        # No exception raised while we expected one
        raise self.fail("Expected to raise {0}, didn't get an exception at all".format(expected_exception.__name__))

    def object_equality_test(self, obj, attr_list, ctor_kwargs=None):
        """ Helper function to easily implement object equality tests.
            Creates an object clone for every passed attribute and checks for (in)equality
            of the original object with the clone based on those attributes' values.
            This function assumes all attributes in `attr_list` can be passed to the ctor of `obj.__class__`.
        """
        if not ctor_kwargs:
            ctor_kwargs = {}

        attr_kwargs = {}
        for attr in attr_list:
            attr_kwargs[attr] = getattr(obj, attr)

        # For every attr, clone the object and assert the clone and the original object are equal
        # Then, change the current attr and assert objects are unequal
        for attr in attr_list:
            attr_kwargs_copy = copy.deepcopy(attr_kwargs)
            attr_kwargs_copy.update(ctor_kwargs)
            clone = obj.__class__(**attr_kwargs_copy)
            self.assertEqual(obj, clone)

            # Change attribute and assert objects are different (via both attribute set and ctor)
            setattr(clone, attr, u"föo")
            self.assertNotEqual(obj, clone)
            attr_kwargs_copy[attr] = u"föo"

            self.assertNotEqual(obj, obj.__class__(**attr_kwargs_copy))


class LogCapture(logging.Handler):
    """ Mock logging handler used to capture any log messages during tests."""

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.messages = []

    def emit(self, record):
        self.messages.append(ustr(self.format(record)))
