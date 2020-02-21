# -*- coding: utf-8 -*-

import os

from click.testing import CliRunner

try:
    # python 2.x
    from mock import patch
except ImportError:
    # python 3.x
    from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import hooks
from gitlint import config


class CLIHookTests(BaseTestCase):
    USAGE_ERROR_CODE = 253
    GIT_CONTEXT_ERROR_CODE = 254
    CONFIG_ERROR_CODE = 255

    def setUp(self):
        super(CLIHookTests, self).setUp()
        self.cli = CliRunner()

        # Patch gitlint.cli.git_version() so that we don't have to patch it separately in every test
        self.git_version_path = patch('gitlint.cli.git_version')
        cli.git_version = self.git_version_path.start()
        cli.git_version.return_value = "git version 1.2.3"

    def tearDown(self):
        self.git_version_path.stop()

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
