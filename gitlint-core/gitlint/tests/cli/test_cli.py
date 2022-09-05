import io
import os
import sys
import platform

import arrow

from io import StringIO

from click.testing import CliRunner

from unittest.mock import patch

from gitlint.shell import CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import __version__
from gitlint.utils import DEFAULT_ENCODING


class CLITests(BaseTestCase):
    USAGE_ERROR_CODE = 253
    GIT_CONTEXT_ERROR_CODE = 254
    CONFIG_ERROR_CODE = 255
    GITLINT_SUCCESS_CODE = 0

    def setUp(self):
        super().setUp()
        self.cli = CliRunner()

        # Patch gitlint.cli.git_version() so that we don't have to patch it separately in every test
        self.git_version_path = patch("gitlint.cli.git_version")
        cli.git_version = self.git_version_path.start()
        cli.git_version.return_value = "git version 1.2.3"

    def tearDown(self):
        self.git_version_path.stop()

    @staticmethod
    def get_system_info_dict():
        """Returns a dict with items related to system values logged by `gitlint --debug`"""
        return {
            "platform": platform.platform(),
            "python_version": sys.version,
            "gitlint_version": __version__,
            "GITLINT_USE_SH_LIB": BaseTestCase.GITLINT_USE_SH_LIB,
            "target": os.path.realpath(os.getcwd()),
            "DEFAULT_ENCODING": DEFAULT_ENCODING,
        }

    def test_version(self):
        """Test for --version option"""
        result = self.cli.invoke(cli.cli, ["--version"])
        self.assertEqual(result.output.split("\n")[0], f"cli, version {__version__}")

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_lint(self, sh, _):
        """Test for basic simple linting functionality"""
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360",
            "test åuthor\x00test-email@föo.com\x002016-12-03 15:28:15 +0100\x00åbc\ncommït-title\n\ncommït-body",
            "#",  # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",
            "file1.txt\npåth/to/file2.txt\n",
        ]

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli)
            self.assertEqual(stderr.getvalue(), '3: B5 Body message is too short (11<20): "commït-body"\n')
            self.assertEqual(result.exit_code, 1)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_lint_multiple_commits(self, sh, _):
        """Test for --commits option"""

        # fmt: off
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n" +
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            "test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            "commït-title1\n\ncommït-body1",
            "#",                                           # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",      # git branch --contains <sha>
            "commit-1/file-1\ncommit-1/file-2\n",          # git diff-tree
                                                            # git log --pretty <FORMAT> <SHA>
            "test åuthor2\x00test-email3@föo.com\x002016-12-04 15:28:15 +0100\x00åbc\n"
            "commït-title2\n\ncommït-body2",
            "commit-2-branch-1\ncommit-2-branch-2\n",      # git branch --contains <sha>
            "commit-2/file-1\ncommit-2/file-2\n",          # git diff-tree
                                                            # git log --pretty <FORMAT> <SHA>
            "test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 +0100\x00åbc\n"
            "commït-title3\n\ncommït-body3",
            "commit-3-branch-1\ncommit-3-branch-2\n",      # git branch --contains <sha>
            "commit-3/file-1\ncommit-3/file-2\n",          # git diff-tree
        ]
        # fmt: on

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar"])
            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_lint_multiple_commits_1"))
            self.assertEqual(result.exit_code, 3)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_lint_multiple_commits_config(self, sh, _):
        """Test for --commits option where some of the commits have gitlint config in the commit message"""

        # fmt: off
        # Note that the second commit title has a trailing period that is being ignored by gitlint-ignore: T3
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n" +
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            "test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            "commït-title1\n\ncommït-body1",
            "#",                                           # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",      # git branch --contains <sha>
            "commit-1/file-1\ncommit-1/file-2\n",          # git diff-tree
                                                            # git log --pretty <FORMAT> <SHA>
            "test åuthor2\x00test-email2@föo.com\x002016-12-04 15:28:15 +0100\x00åbc\n"
            "commït-title2.\n\ncommït-body2\ngitlint-ignore: T3\n",
            "commit-2-branch-1\ncommit-2-branch-2\n",      # git branch --contains <sha>
            "commit-2/file-1\ncommit-2/file-2\n",          # git diff-tree
                                                            # git log --pretty <FORMAT> <SHA>
            "test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 +0100\x00åbc\n"
            "commït-title3.\n\ncommït-body3",
            "commit-3-branch-1\ncommit-3-branch-2\n",      # git branch --contains <sha>
            "commit-3/file-1\ncommit-3/file-2\n",          # git diff-tree
        ]
        # fmt: on

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar"])
            # We expect that the second commit has no failures because of 'gitlint-ignore: T3' in its commit msg body
            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_lint_multiple_commits_config_1"))
            self.assertEqual(result.exit_code, 3)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_lint_multiple_commits_configuration_rules(self, sh, _):
        """Test for --commits option where where we have configured gitlint to ignore certain rules for certain commits"""

        # fmt: off
        # Note that the second commit
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n" +
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            "test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            "commït-title1\n\ncommït-body1",
            "#",                                           # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",      # git branch --contains <sha>
            "commit-1/file-1\ncommit-1/file-2\n",          # git diff-tree
                                                            # git log --pretty <FORMAT> <SHA>
            "test åuthor2\x00test-email3@föo.com\x002016-12-04 15:28:15 +0100\x00åbc\n"
            # Normally T3 violation (trailing punctuation), but this commit is ignored because of
            # config below
            "commït-title2.\n\ncommït-body2\n",
            "commit-2-branch-1\ncommit-2-branch-2\n",      # git branch --contains <sha>
            "commit-2/file-1\ncommit-2/file-2\n",          # git diff-tree
                                                            # git log --pretty <FORMAT> <SHA>
            "test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 +0100\x00åbc\n"
            # Normally T1 and B5 violations, now only T1 because we're ignoring B5 in config below
            "commït-title3.\n\ncommït-body3 foo",
            "commit-3-branch-1\ncommit-3-branch-2\n",      # git branch --contains <sha>
            "commit-3/file-1\ncommit-3/file-2\n",          # git diff-tree
        ]
        # fmt: on

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(
                cli.cli,
                [
                    "--commits",
                    "foo...bar",
                    "-c",
                    "I1.regex=^commït-title2(.*)",
                    "-c",
                    "I2.regex=^commït-body3(.*)",
                    "-c",
                    "I2.ignore=B5",
                ],
            )
            # We expect that the second commit has no failures because of it matching against I1.regex
            # Because we do test for the 3th commit to return violations, this test also ensures that a unique
            # config object is passed to each commit lint call
            expected = (
                "Commit 6f29bf81a8:\n"
                '3: B5 Body message is too short (12<20): "commït-body1"\n\n'
                "Commit 4da2656b0d:\n"
                '1: T3 Title has trailing punctuation (.): "commït-title3."\n'
            )
            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 2)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_lint_commit(self, sh, _):
        """Test for --commit option"""

        # fmt: off
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360\n",  # git log -1 <SHA> --pretty=%H
            # git log --pretty <FORMAT> <SHA>
            "test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            "WIP: commït-title1\n\ncommït-body1",
            "#",                                           # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",      # git branch --contains <sha>
            "commit-1/file-1\ncommit-1/file-2\n",          # git diff-tree
        ]
        # fmt: on

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commit", "foo"])
            self.assertEqual(result.output, "")

            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_lint_commit_1"))
            self.assertEqual(result.exit_code, 2)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_lint_commit_negative(self, sh, _):
        """Negative test for --commit option"""

        # Try using --commit and --commits at the same time (not allowed)
        result = self.cli.invoke(cli.cli, ["--commit", "foo", "--commits", "foo...bar"])
        expected_output = "Error: --commit and --commits are mutually exclusive, use one or the other.\n"
        self.assertEqual(result.output, expected_output)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tïtle \n")
    def test_input_stream(self, _):
        """Test for linting when a message is passed via stdin"""
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli)
            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_input_stream_1"))
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tïtle \n")
    def test_input_stream_debug(self, _):
        """Test for linting when a message is passed via stdin, and debug is enabled.
        This tests specifically that git commit meta is not fetched when not passing --staged"""
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--debug"])
            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_input_stream_debug_1"))
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")
            expected_kwargs = self.get_system_info_dict()
            expected_logs = self.get_expected("cli/test_cli/test_input_stream_debug_2", expected_kwargs)
            self.assert_logged(expected_logs)

    @patch("gitlint.cli.get_stdin_data", return_value="Should be ignored\n")
    @patch("gitlint.git.sh")
    def test_lint_ignore_stdin(self, sh, stdin_data):
        """Test for ignoring stdin when --ignore-stdin flag is enabled"""
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360",
            "test åuthor\x00test-email@föo.com\x002016-12-03 15:28:15 +0100\x00åbc\ncommït-title\n\ncommït-body",
            "#",  # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",  # git branch --contains <sha>
            "file1.txt\npåth/to/file2.txt\n",  # git diff-tree
        ]

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--ignore-stdin"])
            self.assertEqual(stderr.getvalue(), '3: B5 Body message is too short (11<20): "commït-body"\n')
            self.assertEqual(result.exit_code, 1)

        # Assert that we didn't even try to get the stdin data
        self.assertEqual(stdin_data.call_count, 0)

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tïtle \n")
    @patch("arrow.now", return_value=arrow.get("2020-02-19T12:18:46.675182+01:00"))
    @patch("gitlint.git.sh")
    def test_lint_staged_stdin(self, sh, _, __):
        """Test for ignoring stdin when --ignore-stdin flag is enabled"""

        sh.git.side_effect = [
            "#",  # git config --get core.commentchar
            "föo user\n",  # git config --get user.name
            "föo@bar.com\n",  # git config --get user.email
            "my-branch\n",  # git rev-parse --abbrev-ref HEAD (=current branch)
            "commit-1/file-1\ncommit-1/file-2\n",  # git diff-tree
        ]

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--debug", "--staged"])
            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_lint_staged_stdin_1"))
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

            expected_kwargs = self.get_system_info_dict()
            expected_logs = self.get_expected("cli/test_cli/test_lint_staged_stdin_2", expected_kwargs)
            self.assert_logged(expected_logs)

    @patch("arrow.now", return_value=arrow.get("2020-02-19T12:18:46.675182+01:00"))
    @patch("gitlint.git.sh")
    def test_lint_staged_msg_filename(self, sh, _):
        """Test for ignoring stdin when --ignore-stdin flag is enabled"""

        # fmt: off
        sh.git.side_effect = [
            "#",                                         # git config --get core.commentchar
            "föo user\n",                                # git config --get user.name
            "föo@bar.com\n",                             # git config --get user.email
            "my-branch\n",                               # git rev-parse --abbrev-ref HEAD (=current branch)
            "commit-1/file-1\ncommit-1/file-2\n",        # git diff-tree
        ]
        # fmt: on

        with self.tempdir() as tmpdir:
            msg_filename = os.path.join(tmpdir, "msg")
            with open(msg_filename, "w", encoding=DEFAULT_ENCODING) as f:
                f.write("WIP: msg-filename tïtle\n")

            with patch("gitlint.display.stderr", new=StringIO()) as stderr:
                result = self.cli.invoke(cli.cli, ["--debug", "--staged", "--msg-filename", msg_filename])
                self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_lint_staged_msg_filename_1"))
                self.assertEqual(result.exit_code, 2)
                self.assertEqual(result.output, "")

                expected_kwargs = self.get_system_info_dict()
                expected_logs = self.get_expected("cli/test_cli/test_lint_staged_msg_filename_2", expected_kwargs)
                self.assert_logged(expected_logs)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    def test_lint_staged_negative(self, _):
        result = self.cli.invoke(cli.cli, ["--staged"])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        self.assertEqual(
            result.output,
            "Error: The 'staged' option (--staged) can only be used when using "
            "'--msg-filename' or when piping data to gitlint via stdin.\n",
        )

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_fail_without_commits(self, sh, _):
        """Test for --debug option"""

        sh.git.side_effect = ["", ""]  # First invocation of git rev-list  # Second invocation of git rev-list

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            # By default, gitlint should silently exit with code GITLINT_SUCCESS when there are no commits
            result = self.cli.invoke(cli.cli, ["--commits", "foo..bar"])
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(result.exit_code, cli.GITLINT_SUCCESS)
            self.assert_log_contains('DEBUG: gitlint.cli No commits in range "foo..bar"')

            # When --fail-without-commits is set, gitlint should hard fail with code USAGE_ERROR_CODE
            self.clearlog()
            result = self.cli.invoke(cli.cli, ["--commits", "foo..bar", "--fail-without-commits"])
            self.assertEqual(result.output, 'Error: No commits in range "foo..bar"\n')
            self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
            self.assert_log_contains('DEBUG: gitlint.cli No commits in range "foo..bar"')

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    def test_msg_filename(self, _):
        expected_output = "3: B6 Body message is missing\n"

        with self.tempdir() as tmpdir:
            msg_filename = os.path.join(tmpdir, "msg")
            with open(msg_filename, "w", encoding=DEFAULT_ENCODING) as f:
                f.write("Commït title\n")

            with patch("gitlint.display.stderr", new=StringIO()) as stderr:
                result = self.cli.invoke(cli.cli, ["--msg-filename", msg_filename])
                self.assertEqual(stderr.getvalue(), expected_output)
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(result.output, "")

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tïtle \n")
    def test_silent_mode(self, _):
        """Test for --silent option"""
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--silent"])
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tïtle \n")
    def test_verbosity(self, _):
        """Test for --verbosity option"""
        # We only test -v and -vv, more testing is really not required here
        # -v
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-v"])
            self.assertEqual(stderr.getvalue(), "1: T2\n1: T5\n3: B6\n")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

        # -vv
        expected_output = (
            "1: T2 Title has trailing whitespace\n"
            + "1: T5 Title contains the word 'WIP' (case-insensitive)\n"
            + "3: B6 Body message is missing\n"
        )

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-vv"], input="WIP: tïtle \n")
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

        # -vvvv: not supported -> should print a config error
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-vvvv"], input="WIP: tïtle \n")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(result.exit_code, CLITests.CONFIG_ERROR_CODE)
            self.assertEqual(result.output, "Config Error: Option 'verbosity' must be set between 0 and 3\n")

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_debug(self, sh, _):
        """Test for --debug option"""

        # fmt: off
        sh.git.side_effect = [
            "6f29bf81a8322a04071bb794666e48c443a90360\n"  # git rev-list <SHA>
            "25053ccec5e28e1bb8f7551fdbb5ab213ada2401\n"
            "4da2656b0dadc76c7ee3fd0243a96cb64007f125\n",
            # git log --pretty <FORMAT> <SHA>
            "test åuthor1\x00test-email1@föo.com\x002016-12-03 15:28:15 +0100\x00abc\n"
            "commït-title1\n\ncommït-body1",
            "#",                                         # git config --get core.commentchar
            "commit-1-branch-1\ncommit-1-branch-2\n",    # git branch --contains <sha>
            "commit-1/file-1\ncommit-1/file-2\n",        # git diff-tree
            "test åuthor2\x00test-email2@föo.com\x002016-12-04 15:28:15 +0100\x00abc\n"
            "commït-title2.\n\ncommït-body2",
            "commit-2-branch-1\ncommit-2-branch-2\n",    # git branch --contains <sha>
            "commit-2/file-1\ncommit-2/file-2\n",        # git diff-tree
            "test åuthor3\x00test-email3@föo.com\x002016-12-05 15:28:15 +0100\x00abc\n"
            "föobar\nbar",
            "commit-3-branch-1\ncommit-3-branch-2\n",     # git branch --contains <sha>
            "commit-3/file-1\ncommit-3/file-2\n",         # git diff-tree
        ]
        # fmt: on

        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            config_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
            result = self.cli.invoke(cli.cli, ["--config", config_path, "--debug", "--commits", "foo...bar"])

            expected = (
                "Commit 6f29bf81a8:\n3: B5\n\n"
                "Commit 25053ccec5:\n1: T3\n3: B5\n\n"
                "Commit 4da2656b0d:\n2: B4\n3: B5\n3: B6\n"
            )

            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 6)

            expected_kwargs = self.get_system_info_dict()
            expected_kwargs.update({"config_path": config_path})
            expected_logs = self.get_expected("cli/test_cli/test_debug_1", expected_kwargs)
            self.assert_logged(expected_logs)

    @patch("gitlint.cli.get_stdin_data", return_value="Test tïtle\n")
    def test_extra_path(self, _):
        """Test for --extra-path flag"""
        # Test extra-path pointing to a directory
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            extra_path = self.get_sample_path("user_rules")
            result = self.cli.invoke(cli.cli, ["--extra-path", extra_path])
            expected_output = '1: UC1 Commit violåtion 1: "Contënt 1"\n' + "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

        # Test extra-path pointing to a file
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            extra_path = self.get_sample_path(os.path.join("user_rules", "my_commit_rules.py"))
            result = self.cli.invoke(cli.cli, ["--extra-path", extra_path])
            expected_output = '1: UC1 Commit violåtion 1: "Contënt 1"\n' + "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

    @patch("gitlint.cli.get_stdin_data", return_value="Test tïtle\n")
    def test_extra_path_environment(self, _):
        """Test for GITLINT_EXTRA_PATH environment variable"""
        # Test setting extra-path to a directory from an environment variable
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            extra_path = self.get_sample_path("user_rules")
            result = self.cli.invoke(cli.cli, env={"GITLINT_EXTRA_PATH": extra_path})

            expected_output = '1: UC1 Commit violåtion 1: "Contënt 1"\n' + "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

        # Test extra-path pointing to a file from an environment variable
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            extra_path = self.get_sample_path(os.path.join("user_rules", "my_commit_rules.py"))
            result = self.cli.invoke(cli.cli, env={"GITLINT_EXTRA_PATH": extra_path})
            expected_output = '1: UC1 Commit violåtion 1: "Contënt 1"\n' + "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

    @patch("gitlint.cli.get_stdin_data", return_value="Test tïtle\n\nMy body that is long enough")
    def test_contrib(self, _):
        # Test enabled contrib rules
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--contrib", "contrib-title-conventional-commits,CC1"])
            expected_output = self.get_expected("cli/test_cli/test_contrib_1")
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

    @patch("gitlint.cli.get_stdin_data", return_value="Test tïtle\n")
    def test_contrib_negative(self, _):
        result = self.cli.invoke(cli.cli, ["--contrib", "föobar,CC1"])
        self.assertEqual(result.output, "Config Error: No contrib rule with id or name 'föobar' found.\n")
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tëst")
    def test_config_file(self, _):
        """Test for --config option"""
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            config_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
            result = self.cli.invoke(cli.cli, ["--config", config_path])
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5\n3: B6\n")
            self.assertEqual(result.exit_code, 2)

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tëst")
    def test_config_file_environment(self, _):
        """Test for GITLINT_CONFIG environment variable"""
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            config_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
            result = self.cli.invoke(cli.cli, env={"GITLINT_CONFIG": config_path})
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5\n3: B6\n")
            self.assertEqual(result.exit_code, 2)

    def test_config_file_negative(self):
        """Negative test for --config option"""
        # Directory as config file
        config_path = self.get_sample_path("config")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = f"Error: Invalid value for '-C' / '--config': File '{config_path}' is a directory."
        self.assertEqual(result.output.split("\n")[3], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Non existing file
        config_path = self.get_sample_path("föo")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = f"Error: Invalid value for '-C' / '--config': File '{config_path}' does not exist."
        self.assertEqual(result.output.split("\n")[3], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Invalid config file
        config_path = self.get_sample_path(os.path.join("config", "invalid-option-value"))
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    def test_config_file_negative_environment(self):
        """Negative test for GITLINT_CONFIG environment variable"""
        # Directory as config file
        config_path = self.get_sample_path("config")
        result = self.cli.invoke(cli.cli, env={"GITLINT_CONFIG": config_path})
        expected_string = f"Error: Invalid value for '-C' / '--config': File '{config_path}' is a directory."
        self.assertEqual(result.output.split("\n")[3], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Non existing file
        config_path = self.get_sample_path("föo")
        result = self.cli.invoke(cli.cli, env={"GITLINT_CONFIG": config_path})
        expected_string = f"Error: Invalid value for '-C' / '--config': File '{config_path}' does not exist."
        self.assertEqual(result.output.split("\n")[3], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Invalid config file
        config_path = self.get_sample_path(os.path.join("config", "invalid-option-value"))
        result = self.cli.invoke(cli.cli, env={"GITLINT_CONFIG": config_path})
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    def test_target(self, _):
        """Test for the --target option"""
        with self.tempdir() as tmpdir:
            tmpdir_path = os.path.realpath(tmpdir)
            os.environ["LANGUAGE"] = "C"  # Force language to english so we can check for error message
            result = self.cli.invoke(cli.cli, ["--target", tmpdir_path])
            # We expect gitlint to tell us that /tmp is not a git repo (this proves that it takes the target parameter
            # into account).
            self.assertEqual(result.output, "%s is not a git repository.\n" % tmpdir_path)
            self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)

    def test_target_negative(self):
        """Negative test for the --target option"""
        # try setting a non-existing target
        result = self.cli.invoke(cli.cli, ["--target", "/föo/bar"])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Error: Invalid value for '--target': Directory '/föo/bar' does not exist."
        self.assertEqual(result.output.split("\n")[3], expected_msg)

        # try setting a file as target
        target_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
        result = self.cli.invoke(cli.cli, ["--target", target_path])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = f"Error: Invalid value for '--target': Directory '{target_path}' is a file."
        self.assertEqual(result.output.split("\n")[3], expected_msg)

    @patch("gitlint.config.LintConfigGenerator.generate_config")
    def test_generate_config(self, generate_config):
        """Test for the generate-config subcommand"""
        result = self.cli.invoke(cli.cli, ["generate-config"], input="tëstfile\n")
        self.assertEqual(result.exit_code, self.GITLINT_SUCCESS_CODE)
        expected_msg = (
            "Please specify a location for the sample gitlint config file [.gitlint]: tëstfile\n"
            + f"Successfully generated {os.path.realpath('tëstfile')}\n"
        )
        self.assertEqual(result.output, expected_msg)
        generate_config.assert_called_once_with(os.path.realpath("tëstfile"))

    def test_generate_config_negative(self):
        """Negative test for the generate-config subcommand"""
        # Non-existing directory
        fake_dir = os.path.abspath("/föo")
        fake_path = os.path.join(fake_dir, "bar")
        result = self.cli.invoke(cli.cli, ["generate-config"], input=fake_path)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = (
            f"Please specify a location for the sample gitlint config file [.gitlint]: {fake_path}\n"
            + f"Error: Directory '{fake_dir}' does not exist.\n"
        )
        self.assertEqual(result.output, expected_msg)

        # Existing file
        sample_path = self.get_sample_path(os.path.join("config", "gitlintconfig"))
        result = self.cli.invoke(cli.cli, ["generate-config"], input=sample_path)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = (
            "Please specify a location for the sample gitlint "
            f"config file [.gitlint]: {sample_path}\n"
            f'Error: File "{sample_path}" already exists.\n'
        )
        self.assertEqual(result.output, expected_msg)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_git_error(self, sh, _):
        """Tests that the cli handles git errors properly"""
        sh.git.side_effect = CommandNotFound("git")
        result = self.cli.invoke(cli.cli)
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)

    @patch("gitlint.cli.get_stdin_data", return_value=False)
    @patch("gitlint.git.sh")
    def test_no_commits_in_range(self, sh, _):
        """Test for --commits with the specified range being empty."""
        sh.git.side_effect = lambda *_args, **_kwargs: ""
        result = self.cli.invoke(cli.cli, ["--commits", "main...HEAD"])

        self.assert_log_contains('DEBUG: gitlint.cli No commits in range "main...HEAD"')
        self.assertEqual(result.exit_code, self.GITLINT_SUCCESS_CODE)

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: tëst tïtle")
    def test_named_rules(self, _):
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            config_path = self.get_sample_path(os.path.join("config", "named-rules"))
            result = self.cli.invoke(cli.cli, ["--config", config_path, "--debug"])
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), self.get_expected("cli/test_cli/test_named_rules_1"))
            self.assertEqual(result.exit_code, 4)

            # Assert debug logs are correct
            expected_kwargs = self.get_system_info_dict()
            expected_kwargs.update({"config_path": config_path})
            expected_logs = self.get_expected("cli/test_cli/test_named_rules_2", expected_kwargs)
            self.assert_logged(expected_logs)
