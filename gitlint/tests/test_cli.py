from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import __version__

from click.testing import CliRunner
from mock import patch
from StringIO import StringIO


class CLITests(BaseTestCase):
    CONFIG_ERROR_CODE = 10000

    def setUp(self):
        self.cli = CliRunner()

    def assert_output_line(self, output, index, sample_filename, error_line, expected_error):
        expected_output = "{0}:{1}: {2}".format(self.get_sample_path(sample_filename), error_line, expected_error)
        self.assertEqual(output.split("\n")[index], expected_output)

    def test_version(self):
        result = self.cli.invoke(cli.cli, ["--version"])
        self.assertEqual(result.output.split("\n")[0], "cli, version {0}".format(__version__))

    def test_config_file(self):
        config_path = self.get_sample_path("config/gitlintconfig")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        self.assertEqual(result.exit_code, 1)  # single error: empty body
        self.assertEqual(result.output, "Using config from {}\n".format(config_path))

    def test_config_file_negative(self):
        config_path = self.get_sample_path("foo")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = "Error: Invalid value for \"-C\" / \"--config\": Path \"{0}\" does not exist.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[2], expected_string)

    def test_input_stream(self):
        expected_output = "1: T2 Title has trailing whitespace: \"WIP: title \"\n" + \
                          "1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: title \"\n" + \
                          "3: B6 Body message is missing\n"

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, input='WIP: title \n')
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 3)
