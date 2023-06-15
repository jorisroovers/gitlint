import contextlib
import copy
import logging
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import patch

from gitlint.config import LintConfig
from gitlint.deprecation import LOG as DEPRECATION_LOG
from gitlint.deprecation import Deprecation
from gitlint.git import GitChangedFileStats, GitContext
from gitlint.utils import FILE_ENCODING, LOG_FORMAT

EXPECTED_REGEX_STYLE_SEARCH_DEPRECATION_WARNING = (
    "WARNING: gitlint.deprecated.regex_style_search {0} - {1}: gitlint will be switching from using "
    "Python regex 'match' (match beginning) to 'search' (match anywhere) semantics. "
    "Please review your {1}.regex option accordingly. "
    "To remove this warning, set general.regex-style-search=True. More details: "
    "https://jorisroovers.github.io/gitlint/configuration/general_options/#regex-style-search"
)


class BaseTestCase(unittest.TestCase):
    """Base class of which all gitlint unit test classes are derived. Provides a number of convenience methods."""

    # In case of assert failures, print the full error message
    maxDiff = None

    # Working directory in which tests in this class are executed
    working_dir = None
    # Originally working dir when the test was started
    original_working_dir = None

    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samples")
    EXPECTED_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "expected")
    GITLINT_USE_SH_LIB = os.environ.get("GITLINT_USE_SH_LIB", "[NOT SET]")

    @classmethod
    def setUpClass(cls):
        # Run tests a temporary directory to shield them from any local git config
        cls.original_working_dir = os.getcwd()
        cls.working_dir = tempfile.mkdtemp()
        os.chdir(cls.working_dir)

    @classmethod
    def tearDownClass(cls):
        # Go back to original working dir and remove our temp working dir
        os.chdir(cls.original_working_dir)
        shutil.rmtree(cls.working_dir)

    def setUp(self):
        self.logcapture = LogCapture()
        self.logcapture.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger("gitlint").setLevel(logging.DEBUG)
        logging.getLogger("gitlint").handlers = [self.logcapture]
        DEPRECATION_LOG.handlers = [self.logcapture]

        # Make sure we don't propagate anything to child loggers, we need to do this explicitly here
        # because if you run a specific test file like test_lint.py, we won't be calling the setupLogging() method
        # in gitlint.cli that normally takes care of this
        # Example test where this matters (for DEPRECATION_LOG):
        # gitlint-core/gitlint/tests/rules/test_configuration_rules.py::ConfigurationRuleTests::test_ignore_by_title
        logging.getLogger("gitlint").propagate = False
        DEPRECATION_LOG.propagate = False

        # Make sure Deprecation has a clean config set at the start of each test.
        # Tests that want to specifically test deprecation should override this.
        Deprecation.config = LintConfig()
        # Normally Deprecation only logs messages once per process.
        # For tests we want to log every time, so we reset the warning_msgs set per test.
        Deprecation.warning_msgs = set()

    @staticmethod
    @contextlib.contextmanager
    def tempdir():
        tmpdir = tempfile.mkdtemp()
        try:
            yield tmpdir
        finally:
            shutil.rmtree(tmpdir)

    @staticmethod
    def get_sample_path(filename: str = "") -> str:
        # Don't join up empty files names because this will add a trailing slash
        if filename == "":
            return BaseTestCase.SAMPLES_DIR

        return os.path.join(BaseTestCase.SAMPLES_DIR, filename)

    @staticmethod
    def get_sample(filename: str = "") -> str:
        """Read and return the contents of a file in gitlint/tests/samples"""
        sample_path = BaseTestCase.get_sample_path(filename)
        return Path(sample_path).read_text(encoding=FILE_ENCODING)

    @staticmethod
    def patch_input(side_effect):
        """Patches the built-in input() with a provided side-effect"""
        module_path = "builtins.input"
        patched_module = patch(module_path, side_effect=side_effect)
        return patched_module

    @staticmethod
    def get_expected(filename: str = "", variable_dict: Optional[Dict[str, Any]] = None) -> str:
        """Utility method to read an expected file from gitlint/tests/expected and return it as a string.
        Optionally replace template variables specified by variable_dict."""
        expected_path = os.path.join(BaseTestCase.EXPECTED_DIR, filename)
        expected = Path(expected_path).read_text(encoding=FILE_ENCODING)

        if variable_dict:
            expected = expected.format(**variable_dict)
        return expected

    @staticmethod
    def get_user_rules_path():
        return os.path.join(BaseTestCase.SAMPLES_DIR, "user_rules")

    @staticmethod
    def gitcontext(commit_msg_str, changed_files=None):
        """Utility method to easily create gitcontext objects based on a given commit msg string and an optional set of
        changed files"""
        with patch("gitlint.git.git_commentchar") as comment_char:
            comment_char.return_value = "#"
            gitcontext = GitContext.from_commit_msg(commit_msg_str)
            commit = gitcontext.commits[-1]
            if changed_files:
                changed_file_stats = {filename: GitChangedFileStats(filename, 8, 3) for filename in changed_files}
                commit.changed_files_stats = changed_file_stats
            return gitcontext

    @staticmethod
    def gitcommit(commit_msg_str, changed_files=None, **kwargs):
        """Utility method to easily create git commit given a commit msg string and an optional set of changed files"""
        gitcontext = BaseTestCase.gitcontext(commit_msg_str, changed_files)
        commit = gitcontext.commits[-1]
        for attr, value in kwargs.items():
            setattr(commit, attr, value)
        return commit

    def assert_logged(self, expected):
        """Asserts that the logs match an expected string or list.
        This method knows how to compare a passed list of log lines as well as a newline concatenated string
        of all loglines."""
        if isinstance(expected, list):
            self.assertListEqual(self.logcapture.messages, expected)
        else:
            self.assertEqual("\n".join(self.logcapture.messages), expected)

    def assert_log_contains(self, line):
        """Asserts that a certain line is in the logs"""
        self.assertIn(line, self.logcapture.messages)

    def assertRaisesRegex(self, expected_exception, expected_regex, *args, **kwargs):
        """Pass-through method to unittest.TestCase.assertRaisesRegex that applies re.escape() to the passed
        `expected_regex`. This is useful to automatically escape all file paths that might be present in the regex.
        """
        return super().assertRaisesRegex(expected_exception, re.escape(expected_regex), *args, **kwargs)

    def clearlog(self):
        """Clears the log capture"""
        self.logcapture.clear()

    @contextlib.contextmanager
    def assertRaisesMessage(self, expected_exception, expected_msg):
        """Asserts an exception has occurred with a given error message"""
        try:
            yield
        except expected_exception as exc:
            exception_msg = str(exc)
            if exception_msg != expected_msg:  # pragma: nocover
                error = f"Right exception, wrong message:\n      got: {exception_msg}\n expected: {expected_msg}"
                raise self.fail(error) from exc
            # else: everything is fine, just return
            return
        except Exception as exc:  # pragma: nocover
            raise self.fail(f"Expected '{expected_exception.__name__}' got '{exc.__class__.__name__}'") from exc

        # No exception raised while we expected one
        raise self.fail(
            f"Expected to raise {expected_exception.__name__}, didn't get an exception at all"
        )  # pragma: nocover

    def object_equality_test(self, obj, attr_list, ctor_kwargs=None):
        """Helper function to easily implement object equality tests.
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
            setattr(clone, attr, "föo")
            self.assertNotEqual(obj, clone)
            attr_kwargs_copy[attr] = "föo"

            self.assertNotEqual(obj, obj.__class__(**attr_kwargs_copy))


class LogCapture(logging.Handler):
    """Mock logging handler used to capture any log messages during tests."""

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))

    def clear(self):
        self.messages = []
