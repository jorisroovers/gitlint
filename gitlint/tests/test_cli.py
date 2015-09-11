from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import __version__

from click.testing import CliRunner


class CLITests(BaseTestCase):
    def setUp(self):
        self.cli = CliRunner()

    def assert_output_line(self, output, index, sample_filename, error_line, expected_error):
        expected_output = "{0}:{1}: {2}".format(self.get_sample_path(sample_filename), error_line, expected_error)
        self.assertEqual(output.split("\n")[index], expected_output)

    def test_version(self):
        result = self.cli.invoke(cli.cli, ["--version"])
        self.assertEqual(result.output.split("\n")[0], "cli, version {0}".format(__version__))

    def test_config_file_negative(self):
        args = ["--config", self.get_sample_path("foo"), self.get_sample_path("sample1.md")]
        result = self.cli.invoke(cli.cli, args)
        expected_string = "Error: Invalid value for \"-C\" / \"--config\": Path \"{0}\" does not exist.".format(
            self.get_sample_path("foo"))
        self.assertEqual(result.output.split("\n")[2], expected_string)
