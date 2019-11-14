# -*- coding: utf-8 -*-

import contextlib
import io
import os
import sys
import platform
import shutil
import tempfile

try:
    # python 2.x
    from StringIO import StringIO
except ImportError:
    # python 3.x
    from io import StringIO  # pylint: disable=ungrouped-imports

from click.testing import CliRunner

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.shell import CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import hooks
from gitlint import __version__
from gitlint import config
from gitlint.utils import DEFAULT_ENCODING


@contextlib.contextmanager
def tempdir():
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)


class CLITests(BaseTestCase):
    USAGE_ERROR_CODE = 253
    GIT_CONTEXT_ERROR_CODE = 254
    CONFIG_ERROR_CODE = 255

    def setUp(self):
        super(CLITests, self).setUp()
        self.cli = CliRunner()

        # Patch gitlint.cli.git_version() so that we don't have to patch it separately in every test
        self.git_version_path = patch('gitlint.cli.git_version')
        cli.git_version = self.git_version_path.start()
        cli.git_version.return_value = "git version 1.2.3"

    def tearDown(self):
        self.git_version_path.stop()

    def test_version(self):
        """ Test for --version option """
        result = self.cli.invoke(cli.cli, ["--version"])
        self.assertEqual(result.output.split("\n")[0], "cli, version {0}".format(__version__))

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint(self, sh, _):
        """ Test for basic simple linting functionality """
        sh.git.side_effect = self.GIT_CONFIG_SIDE_EFFECTS + [
            "6f29bf81a8322a04071bb794666e48c443a90360",
            u"test åuthor\x00test-email@föo.com\x002016-12-03 15:28:15 01:00\x00åbc\n"
            u"commït-title\n\ncommït-body",
            u"file1.txt\npåth/to/file2.txt\n"
        ]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli)
            self.assertEqual(stderr.getvalue(), u'3: B5 Body message is too short (11<20): "commït-body"\n')
            self.assertEqual(result.exit_code, 1)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint_multiple_commits(self, sh, _):
        """ Test for --commits option """

        sh.git.side_effect = self.GIT_CONFIG_SIDE_EFFECTS + [
            "6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n" +
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            u"test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 01 :00\x00åbc\n"
            u"commït-title1\n\ncommït-body1",
            u"file1.txt\npåth/to/file2.txt\n",  # git diff-tree <SHA>
            u"test åuthor2\x00test-email3@föo.com\x002016-12-04 15:28:15 01:00\x00åbc\n"
            u"commït-title2\n\ncommït-body2",
            u"file4.txt\npåth/to/file5.txt\n",
            u"test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 01:00\x00åbc\n"
            u"commït-title3\n\ncommït-body3",
            u"file6.txt\npåth/to/file7.txt\n"
        ]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar"])
            self.assertEqual(stderr.getvalue(), self.get_expected("test_cli/test_lint_multiple_commits_1"))
            self.assertEqual(result.exit_code, 3)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint_multiple_commits_config(self, sh, _):
        """ Test for --commits option where some of the commits have gitlint config in the commit message """

        # Note that the second commit title has a trailing period that is being ignored by gitlint-ignore: T3
        sh.git.side_effect = self.GIT_CONFIG_SIDE_EFFECTS + [
            "6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n" +
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            u"test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 01:00\x00åbc\n"
            u"commït-title1\n\ncommït-body1",
            u"file1.txt\npåth/to/file2.txt\n",  # git diff-tree <SHA>
            u"test åuthor2\x00test-email3@föo.com\x002016-12-04 15:28:15 01:00\x00åbc\n"
            u"commït-title2.\n\ncommït-body2\ngitlint-ignore: T3\n",
            u"file4.txt\npåth/to/file5.txt\n",
            u"test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 01:00\x00åbc\n"
            u"commït-title3.\n\ncommït-body3",
            u"file6.txt\npåth/to/file7.txt\n"
        ]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar"])
            # We expect that the second commit has no failures because of 'gitlint-ignore: T3' in its commit msg body
            self.assertEqual(stderr.getvalue(), self.get_expected("test_cli/test_lint_multiple_commits_config_1"))
            self.assertEqual(result.exit_code, 3)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint_multiple_commits_configuration_rules(self, sh, _):
        """ Test for --commits option where where we have configured gitlint to ignore certain rules for certain commits
        """

        # Note that the second commit
        sh.git.side_effect = self.GIT_CONFIG_SIDE_EFFECTS + [
            "6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n" +
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            u"test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 01:00\x00åbc\n"
            u"commït-title1\n\ncommït-body1",
            u"file1.txt\npåth/to/file2.txt\n",  # git diff-tree <SHA>
            u"test åuthor2\x00test-email3@föo.com\x002016-12-04 15:28:15 01:00\x00åbc\n"
            # Normally T3 violation (trailing punctuation), but this commit is ignored because of
            # config below
            u"commït-title2.\n\ncommït-body2\n",
            u"file4.txt\npåth/to/file5.txt\n",
            u"test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 01:00\x00åbc\n"
            # Normally T1 and B5 violations, now only T1 because we're ignoring B5 in config below
            u"commït-title3.\n\ncommït-body3 foo",
            u"file6.txt\npåth/to/file7.txt\n"
        ]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar", "-c", "I1.regex=^commït-title2(.*)",
                                               "-c", "I2.regex=^commït-body3(.*)", "-c", "I2.ignore=B5"])
            # We expect that the second commit has no failures because of it matching against I1.regex
            # Because we do test for the 3th commit to return violations, this test also ensures that a unique
            # config object is passed to each commit lint call
            expected = (u"Commit 6f29bf81a8:\n"
                        u'3: B5 Body message is too short (12<20): "commït-body1"\n\n'
                        u"Commit 4da2656b0d:\n"
                        u'1: T3 Title has trailing punctuation (.): "commït-title3."\n')
            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 2)

    @patch('gitlint.cli.get_stdin_data', return_value=u'WIP: tïtle \n')
    def test_input_stream(self, _):
        """ Test for linting when a message is passed via stdin """
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli)
            self.assertEqual(stderr.getvalue(), self.get_expected("test_cli/test_input_stream_1"))
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

    @patch('gitlint.cli.get_stdin_data', return_value="Should be ignored\n")
    @patch('gitlint.git.sh')
    def test_lint_ignore_stdin(self, sh, stdin_data):
        """ Test for ignoring stdin when --ignore-stdin flag is enabled"""
        sh.git.side_effect = self.GIT_CONFIG_SIDE_EFFECTS + [
            "6f29bf81a8322a04071bb794666e48c443a90360",
            u"test åuthor\x00test-email@föo.com\x002016-12-03 15:28:15 01:00\x00åbc\n"
            u"commït-title\n\ncommït-body",
            u"file1.txt\npåth/to/file2.txt\n"
        ]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--ignore-stdin"])
            self.assertEqual(stderr.getvalue(), u'3: B5 Body message is too short (11<20): "commït-body"\n')
            self.assertEqual(result.exit_code, 1)

        # Assert that we didn't even try to get the stdin data
        self.assertEqual(stdin_data.call_count, 0)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    def test_msg_filename(self, _):
        expected_output = u"3: B6 Body message is missing\n"

        with tempdir() as tmpdir:
            msg_filename = os.path.join(tmpdir, "msg")
            with io.open(msg_filename, 'w', encoding=DEFAULT_ENCODING) as f:
                f.write(u"Commït title\n")

            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                result = self.cli.invoke(cli.cli, ["--msg-filename", msg_filename])
                self.assertEqual(stderr.getvalue(), expected_output)
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(result.output, "")

    @patch('gitlint.cli.get_stdin_data', return_value=u"WIP: tïtle \n")
    def test_silent_mode(self, _):
        """ Test for --silent option """
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--silent"])
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

    @patch('gitlint.cli.get_stdin_data', return_value=u"WIP: tïtle \n")
    def test_verbosity(self, _):
        """ Test for --verbosity option """
        # We only test -v and -vv, more testing is really not required here
        # -v
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-v"])
            self.assertEqual(stderr.getvalue(), "1: T2\n1: T5\n3: B6\n")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

        # -vv
        expected_output = "1: T2 Title has trailing whitespace\n" + \
                          "1: T5 Title contains the word 'WIP' (case-insensitive)\n" + \
                          "3: B6 Body message is missing\n"

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-vv"], input=u"WIP: tïtle \n")
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

        # -vvvv: not supported -> should print a config error
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-vvvv"], input=u'WIP: tïtle \n')
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(result.exit_code, CLITests.CONFIG_ERROR_CODE)
            self.assertEqual(result.output, "Config Error: Option 'verbosity' must be set between 0 and 3\n")

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_debug(self, sh, _):
        """ Test for --debug option """

        sh.git.side_effect = self. GIT_CONFIG_SIDE_EFFECTS + [
            "6f29bf81a8322a04071bb794666e48c443a90360\n"  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n"
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            u"test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 01:00\x00abc\n"
            u"commït-title1\n\ncommït-body1",
            u"file1.txt\npåth/to/file2.txt\n",
            u"test åuthor2\x00test-email2@föo.com\x002016-12-04 15:28:15 01:00\x00abc\n"
            u"commït-title2.\n\ncommït-body2",
            u"file4.txt\npåth/to/file5.txt\n",
            u"test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 01:00\x00abc\n"
            u"föo\nbar",
            u"file6.txt\npåth/to/file7.txt\n"
        ]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            config_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
            result = self.cli.invoke(cli.cli, ["--config", config_path, "--debug", "--commits",
                                               "foo...bar"])

            expected = "Commit 6f29bf81a8:\n3: B5\n\n" + \
                       "Commit 25053ccec5:\n1: T3\n3: B5\n\n" + \
                       "Commit 4da2656b0d:\n2: B4\n3: B5\n3: B6\n"

            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 6)

            expected_kwargs = {'platform': platform.platform(), "python_version": sys.version,
                               'gitlint_version': __version__, 'config_path': config_path,
                               'GITLINT_USE_SH_LIB': self.GITLINT_USE_SH_LIB, 'target': os.path.realpath(os.getcwd())}
            expected_logs = self.get_expected('test_cli/test_debug_1', expected_kwargs)
            self.assert_logged(expected_logs)

    @patch('gitlint.cli.get_stdin_data', return_value=u"Test tïtle\n")
    def test_extra_path(self, _):
        """ Test for --extra-path flag """
        # Test extra-path pointing to a directory
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            extra_path = self.get_sample_path("user_rules")
            result = self.cli.invoke(cli.cli, ["--extra-path", extra_path, "--debug"])
            expected_output = u"1: UC1 Commit violåtion 1: \"Contënt 1\"\n" + \
                              "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

        # Test extra-path pointing to a file
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            extra_path = self.get_sample_path(os.path.join("user_rules", "my_commit_rules.py"))
            result = self.cli.invoke(cli.cli, ["--extra-path", extra_path, "--debug"])
            expected_output = u"1: UC1 Commit violåtion 1: \"Contënt 1\"\n" + \
                              "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

    @patch('gitlint.cli.get_stdin_data', return_value=u"Test tïtle\n\nMy body that is long enough")
    def test_contrib(self, _):
        # Test enabled contrib rules
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--contrib", "contrib-title-conventional-commits,CC1"])
            expected_output = self.get_expected('test_cli/test_contrib_1')
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 3)

    @patch('gitlint.cli.get_stdin_data', return_value=u"Test tïtle\n")
    def test_contrib_negative(self, _):
        result = self.cli.invoke(cli.cli, ["--contrib", u"föobar,CC1"])
        self.assertEqual(result.output, u"Config Error: No contrib rule with id or name 'föobar' found.\n")
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    @patch('gitlint.cli.get_stdin_data', return_value=u"WIP: tëst")
    def test_config_file(self, _):
        """ Test for --config option """
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            config_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
            result = self.cli.invoke(cli.cli, ["--config", config_path])
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5\n3: B6\n")
            self.assertEqual(result.exit_code, 2)

    def test_config_file_negative(self):
        """ Negative test for --config option """
        # Directory as config file
        config_path = self.get_sample_path("config")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = u"Error: Invalid value for \"-C\" / \"--config\": File \"{0}\" is a directory.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[3], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Non existing file
        config_path = self.get_sample_path(u"föo")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = u"Error: Invalid value for \"-C\" / \"--config\": File \"{0}\" does not exist.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[3], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Invalid config file
        config_path = self.get_sample_path(os.path.join("config", "invalid-option-value"))
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    def test_target(self, _):
        """ Test for the --target option """
        os.environ["LANGUAGE"] = "C"  # Force language to english so we can check for error message
        result = self.cli.invoke(cli.cli, ["--target", "/tmp"])
        # We expect gitlint to tell us that /tmp is not a git repo (this proves that it takes the target parameter
        # into account).
        expected_path = os.path.realpath("/tmp")
        self.assertEqual(result.output, "%s is not a git repository.\n" % expected_path)
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)

    def test_target_negative(self):
        """ Negative test for the --target option """
        # try setting a non-existing target
        result = self.cli.invoke(cli.cli, ["--target", u"/föo/bar"])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = u"Error: Invalid value for \"--target\": Directory \"/föo/bar\" does not exist."
        self.assertEqual(result.output.split("\n")[3], expected_msg)

        # try setting a file as target
        target_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
        result = self.cli.invoke(cli.cli, ["--target", target_path])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = u"Error: Invalid value for \"--target\": Directory \"{0}\" is a file.".format(target_path)
        self.assertEqual(result.output.split("\n")[3], expected_msg)

    @patch('gitlint.config.LintConfigGenerator.generate_config')
    def test_generate_config(self, generate_config):
        """ Test for the generate-config subcommand """
        result = self.cli.invoke(cli.cli, ["generate-config"], input=u"tëstfile\n")
        self.assertEqual(result.exit_code, 0)
        expected_msg = u"Please specify a location for the sample gitlint config file [.gitlint]: tëstfile\n" + \
                       u"Successfully generated {0}\n".format(os.path.realpath(u"tëstfile"))
        self.assertEqual(result.output, expected_msg)
        generate_config.assert_called_once_with(os.path.realpath(u"tëstfile"))

    def test_generate_config_negative(self):
        """ Negative test for the generate-config subcommand """
        # Non-existing directory
        fake_dir = os.path.abspath(u"/föo")
        fake_path = os.path.join(fake_dir, u"bar")
        result = self.cli.invoke(cli.cli, ["generate-config"], input=fake_path)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = (u"Please specify a location for the sample gitlint config file [.gitlint]: {0}\n"
                        + u"Error: Directory '{1}' does not exist.\n").format(fake_path, fake_dir)
        self.assertEqual(result.output, expected_msg)

        # Existing file
        sample_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
        result = self.cli.invoke(cli.cli, ["generate-config"], input=sample_path)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Please specify a location for the sample gitlint " + \
                       "config file [.gitlint]: {0}\n".format(sample_path) + \
                       "Error: File \"{0}\" already exists.\n".format(sample_path)
        self.assertEqual(result.output, expected_msg)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_git_error(self, sh, _):
        """ Tests that the cli handles git errors properly """
        sh.git.side_effect = CommandNotFound("git")
        result = self.cli.invoke(cli.cli)
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)

    @patch('gitlint.cli.get_stdin_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_no_commits_in_range(self, sh, _):
        """ Test for --commits with the specified range being empty. """
        sh.git.side_effect = lambda *_args, **_kwargs: ""
        result = self.cli.invoke(cli.cli, ["--commits", "master...HEAD"])

        self.assert_log_contains(u"DEBUG: gitlint.cli No commits in range \"master...HEAD\"")
        self.assertEqual(result.exit_code, 0)

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook')
    @patch('gitlint.hooks.git_hooks_dir', return_value=os.path.join(u"/hür", u"dur"))
    def test_install_hook(self, _, install_hook):
        """ Test for install-hook subcommand """
        result = self.cli.invoke(cli.cli, ["install-hook"])
        expected_path = os.path.join(u"/hür", u"dur", hooks.COMMIT_MSG_HOOK_DST_PATH)
        expected = u"Successfully installed gitlint commit-msg hook in {0}\n".format(expected_path)
        self.assertEqual(result.output, expected)
        self.assertEqual(result.exit_code, 0)
        expected_config = config.LintConfig()
        expected_config.target = os.path.realpath(os.getcwd())
        install_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook')
    @patch('gitlint.hooks.git_hooks_dir', return_value=os.path.join(u"/hür", u"dur"))
    def test_install_hook_target(self, _, install_hook):
        """  Test for install-hook subcommand with a specific --target option specified """
        # Specified target
        result = self.cli.invoke(cli.cli, ["--target", self.SAMPLES_DIR, "install-hook"])
        expected_path = os.path.join(u"/hür", u"dur", hooks.COMMIT_MSG_HOOK_DST_PATH)
        expected = "Successfully installed gitlint commit-msg hook in %s\n" % expected_path
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)

        expected_config = config.LintConfig()
        expected_config.target = self.SAMPLES_DIR
        install_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook', side_effect=hooks.GitHookInstallerError(u"tëst"))
    def test_install_hook_negative(self, install_hook):
        """ Negative test for install-hook subcommand """
        result = self.cli.invoke(cli.cli, ["install-hook"])
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        self.assertEqual(result.output, u"tëst\n")
        expected_config = config.LintConfig()
        expected_config.target = os.path.realpath(os.getcwd())
        install_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook')
    @patch('gitlint.hooks.git_hooks_dir', return_value=os.path.join(u"/hür", u"dur"))
    def test_uninstall_hook(self, _, uninstall_hook):
        """ Test for uninstall-hook subcommand """
        result = self.cli.invoke(cli.cli, ["uninstall-hook"])
        expected_path = os.path.join(u"/hür", u"dur", hooks.COMMIT_MSG_HOOK_DST_PATH)
        expected = u"Successfully uninstalled gitlint commit-msg hook from {0}\n".format(expected_path)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        expected_config = config.LintConfig()
        expected_config.target = os.path.realpath(os.getcwd())
        uninstall_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook', side_effect=hooks.GitHookInstallerError(u"tëst"))
    def test_uninstall_hook_negative(self, uninstall_hook):
        """ Negative test for uninstall-hook subcommand """
        result = self.cli.invoke(cli.cli, ["uninstall-hook"])
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        self.assertEqual(result.output, u"tëst\n")
        expected_config = config.LintConfig()
        expected_config.target = os.path.realpath(os.getcwd())
        uninstall_hook.assert_called_once_with(expected_config)
