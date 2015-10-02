from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import hooks
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

    @patch('gitlint.cli.GitLinter')
    def test_config_file(self, git_linter):
        config_path = self.get_sample_path("config/gitlintconfig")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        self.assertEqual(result.exit_code, 0)
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

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook')
    def test_install_hook(self, install_hook):
        result = self.cli.invoke(cli.cli, ["--install-hook"])
        expected = "Successfully installed gitlint commit-msg hook in {}\n\n".format(hooks.COMMIT_MSG_HOOK_DST_PATH)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        install_hook.assert_called_once_with()

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook', side_effect=hooks.GitHookInstallerError("test"))
    def test_install_hook_negative(self, install_hook):
        result = self.cli.invoke(cli.cli, ["--install-hook"])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, "test\n")
        install_hook.assert_called_once_with()

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook')
    def test_uninstall_hook(self, uninstall_hook):
        result = self.cli.invoke(cli.cli, ["--uninstall-hook"])
        expected = "Successfully uninstalled gitlint commit-msg hook from {0}\n\n".format(
            hooks.COMMIT_MSG_HOOK_DST_PATH)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        uninstall_hook.assert_called_once_with()

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook', side_effect=hooks.GitHookInstallerError("test"))
    def test_uninstall_hook_negative(self, uninstall_hook):
        result = self.cli.invoke(cli.cli, ["--uninstall-hook"])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, "test\n")
        uninstall_hook.assert_called_once_with()
