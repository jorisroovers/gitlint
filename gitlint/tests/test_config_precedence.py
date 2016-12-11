try:
    # python 2.x
    from StringIO import StringIO
except ImportError:
    # python 3.x
    from io import StringIO

from click.testing import CliRunner
from mock import patch

from gitlint.tests.base import BaseTestCase
from gitlint import cli


class LintConfigPrecedenceTests(BaseTestCase):
    def setUp(self):
        self.cli = CliRunner()

    def test_config_precedence(self):
        # TODO(jroovers): this test really only test verbosity, we need to do some refactoring to gitlint.cli
        # to more easily test everything
        # Test that the config precedence is followed:
        # 1. commandline convenience flags
        # 2. commandline -c flags
        # 3. config file
        # 4. default config
        input_text = "WIP\n\nThis is a test message\n"
        config_path = self.get_sample_path("config/gitlintconfig")

        # 1. commandline convenience flags
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-vvv", "-c", "general.verbosity=2", "--config", config_path],
                                     input=input_text)
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP\"\n")

        # 2. commandline -c flags
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-c", "general.verbosity=2", "--config", config_path], input=input_text)
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive)\n")

        # 3. config file
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--config", config_path], input=input_text)
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5\n")

        # 4. default config
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, input=input_text)
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP\"\n")

    def test_ignore_precedence(self):
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            # --ignore takes precedence over -c general.ignore
            result = self.cli.invoke(cli.cli, ["-c", "general.ignore=T5", "--ignore", "B6"],
                                     input="WIP: This is a test")
            self.assertEqual(result.output, "")
            self.assertEqual(result.exit_code, 1)
            # We still expect the T5 violation, but no B6 violation as --ignore overwrites -c general.ignore
            self.assertEqual(stderr.getvalue(),
                             "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: This is a test\"\n")

        # test that we can also still configure a rule that is first ignored but then not
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            # --ignore takes precedence over -c general.ignore
            result = self.cli.invoke(cli.cli, ["-c", "general.ignore=title-max-length",
                                               "-c", "title-max-length.line-length=5",
                                               "--ignore", "B6"], input="This is a test")
            self.assertEqual(result.output, "")
            self.assertEqual(result.exit_code, 1)

            # We still expect the T1 violation with custom config,
            # but no B6 violation as --ignore overwrites -c general.ignore
            self.assertEqual(stderr.getvalue(), "1: T1 Title exceeds max length (14>5): \"This is a test\"\n")
