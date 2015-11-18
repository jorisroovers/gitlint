from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import hooks
from gitlint import __version__
from gitlint import config
from click.testing import CliRunner
from mock import patch
from sh import CommandNotFound
import os

try:
    # python 2.x
    from StringIO import StringIO
except ImportError:
    # python 3.x
    from io import StringIO


class CLITests(BaseTestCase):
    USAGE_ERROR_CODE = 253
    GIT_CONTEXT_ERROR_CODE = 254
    CONFIG_ERROR_CODE = 255

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
        # Directory as config file
        config_path = self.get_sample_path("config")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = "Error: Invalid value for \"-C\" / \"--config\": Path \"{0}\" is a directory.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[2], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Non existing file
        config_path = self.get_sample_path("foo")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = "Error: Invalid value for \"-C\" / \"--config\": Path \"{0}\" does not exist.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[2], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Invalid config file
        config_path = self.get_sample_path("config/invalid-option-value")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    @patch('gitlint.cli.sys')
    def test_target(self, sys):
        sys.stdin.isatty.return_value = True
        result = self.cli.invoke(cli.cli, ["--target", "/tmp"])
        # We expect gitlint to tell us that /tmp is not a git repo (this proves that it takes the target parameter
        # into account).
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        self.assertEqual(result.output, "/tmp is not a git repository.\n")

    def test_target_negative(self):
        # try setting a non-existing target
        result = self.cli.invoke(cli.cli, ["--target", "/foo/bar"])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Error: Invalid value for \"--target\": Directory \"/foo/bar\" does not exist."
        self.assertEqual(result.output.split("\n")[2], expected_msg)

        # try setting a file as target
        target_path = self.get_sample_path("config/gitlintconfig")
        result = self.cli.invoke(cli.cli, ["--target", target_path])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Error: Invalid value for \"--target\": Directory \"{}\" is a file.".format(target_path)
        self.assertEqual(result.output.split("\n")[2], expected_msg)

    @patch('gitlint.config.LintConfigGenerator.generate_config')
    def test_generate_config(self, generate_config):
        result = self.cli.invoke(cli.cli, ["generate-config"], input="testfile\n")
        self.assertEqual(result.exit_code, 0)
        expected_msg = "Please specify a location for the sample gitlint config file [.gitlint]: testfile\n" + \
                       "Successfully generated {}\n".format(os.path.abspath("testfile"))
        self.assertEqual(result.output, expected_msg)
        generate_config.assert_called_once_with(os.path.abspath("testfile"))

    def test_generate_config_negative(self):
        # Non-existing directory
        result = self.cli.invoke(cli.cli, ["generate-config"], input="/foo/bar")
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Please specify a location for the sample gitlint config file [.gitlint]: /foo/bar\n" + \
                       "Error: Directory '/foo' does not exist.\n"
        self.assertEqual(result.output, expected_msg)

        # Existing file
        sample_path = self.get_sample_path("config/gitlintconfig")
        result = self.cli.invoke(cli.cli, ["generate-config"], input=sample_path)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Please specify a location for the sample gitlint " + \
                       "config file [.gitlint]: {}\n".format(sample_path) + \
                       "Error: File \"{}\" already exists.\n".format(sample_path)
        self.assertEqual(result.output, expected_msg)

    @patch('gitlint.git.sh')
    @patch('gitlint.cli.sys')
    def test_git_error(self, sys, sh):
        sys.stdin.isatty.return_value = True
        sh.git.log.side_effect = CommandNotFound("git")
        result = self.cli.invoke(cli.cli)
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)

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
        result = self.cli.invoke(cli.cli, ["install-hook"])
        expected_path = os.path.join(os.getcwd(), hooks.COMMIT_MSG_HOOK_DST_PATH)
        expected = "Successfully installed gitlint commit-msg hook in {}\n".format(expected_path)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        install_hook.assert_called_once_with(config.LintConfig())

        # Specified target
        install_hook.reset_mock()
        result = self.cli.invoke(cli.cli, ["--target", "/tmp", "install-hook"])
        expected = "Successfully installed gitlint commit-msg hook in /tmp/.git/hooks/commit-msg\n"
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        install_hook.assert_called_once_with(config.LintConfig(target="/tmp"))

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook', side_effect=hooks.GitHookInstallerError("test"))
    def test_install_hook_negative(self, install_hook):
        result = self.cli.invoke(cli.cli, ["install-hook"])
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        self.assertEqual(result.output, "test\n")
        install_hook.assert_called_once_with(config.LintConfig())

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook')
    def test_uninstall_hook(self, uninstall_hook):
        result = self.cli.invoke(cli.cli, ["uninstall-hook"])
        expected_path = os.path.join(os.getcwd(), hooks.COMMIT_MSG_HOOK_DST_PATH)
        expected = "Successfully uninstalled gitlint commit-msg hook from {0}\n".format(expected_path)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        uninstall_hook.assert_called_once_with(config.LintConfig())

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook', side_effect=hooks.GitHookInstallerError("test"))
    def test_uninstall_hook_negative(self, uninstall_hook):
        result = self.cli.invoke(cli.cli, ["uninstall-hook"])
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        self.assertEqual(result.output, "test\n")
        uninstall_hook.assert_called_once_with(config.LintConfig())
