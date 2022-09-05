from io import StringIO

from click.testing import CliRunner

from unittest.mock import patch

from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint.config import LintConfigBuilder


class LintConfigPrecedenceTests(BaseTestCase):
    def setUp(self):
        self.cli = CliRunner()

    @patch("gitlint.cli.get_stdin_data", return_value="WIP:fö\n\nThis is å test message\n")
    def test_config_precedence(self, _):
        # TODO(jroovers): this test really only test verbosity, we need to do some refactoring to gitlint.cli
        # to more easily test everything
        # Test that the config precedence is followed:
        # 1. commandline convenience flags
        # 2. environment variables
        # 3. commandline -c flags
        # 4. config file
        # 5. default config
        config_path = self.get_sample_path("config/gitlintconfig")

        # 1. commandline convenience flags
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-vvv", "-c", "general.verbosity=2", "--config", config_path])
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP:fö\"\n")

        # 2. environment variables
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(
                cli.cli, ["-c", "general.verbosity=2", "--config", config_path], env={"GITLINT_VERBOSITY": "3"}
            )
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP:fö\"\n")

        # 3. commandline -c flags
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-c", "general.verbosity=2", "--config", config_path])
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive)\n")

        # 4. config file
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--config", config_path])
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5\n")

        # 5. default config
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli)
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP:fö\"\n")

    @patch("gitlint.cli.get_stdin_data", return_value="WIP: This is å test")
    def test_ignore_precedence(self, get_stdin_data):
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            # --ignore takes precedence over -c general.ignore
            result = self.cli.invoke(cli.cli, ["-c", "general.ignore=T5", "--ignore", "B6"])
            self.assertEqual(result.output, "")
            self.assertEqual(result.exit_code, 1)
            # We still expect the T5 violation, but no B6 violation as --ignore overwrites -c general.ignore
            self.assertEqual(
                stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: This is å test\"\n"
            )

        # test that we can also still configure a rule that is first ignored but then not
        with patch("gitlint.display.stderr", new=StringIO()) as stderr:
            get_stdin_data.return_value = "This is å test"
            # --ignore takes precedence over -c general.ignore
            result = self.cli.invoke(
                cli.cli,
                ["-c", "general.ignore=title-max-length", "-c", "title-max-length.line-length=5", "--ignore", "B6"],
            )
            self.assertEqual(result.output, "")
            self.assertEqual(result.exit_code, 1)

            # We still expect the T1 violation with custom config,
            # but no B6 violation as --ignore overwrites -c general.ignore
            self.assertEqual(stderr.getvalue(), '1: T1 Title exceeds max length (14>5): "This is å test"\n')

    def test_general_option_after_rule_option(self):
        # We used to have a bug where we didn't process general options before setting specific options, this would
        # lead to errors when e.g.: trying to configure a user rule before the rule class was loaded by extra-path
        # This test is here to test for regressions against this.

        config_builder = LintConfigBuilder()
        config_builder.set_option("my-üser-commit-rule", "violation-count", 3)
        user_rules_path = self.get_sample_path("user_rules")
        config_builder.set_option("general", "extra-path", user_rules_path)
        config = config_builder.build()

        self.assertEqual(config.extra_path, user_rules_path)
        self.assertEqual(config.get_rule_option("my-üser-commit-rule", "violation-count"), 3)
