# -*- coding: utf-8 -*-

import os
import sys
import platform

try:
    # python 2.x
    from StringIO import StringIO
except ImportError:
    # python 3.x
    from io import StringIO

from click.testing import CliRunner
from mock import patch
from sh import CommandNotFound

from gitlint.tests.base import BaseTestCase
from gitlint import cli
from gitlint import hooks
from gitlint import __version__
from gitlint import config


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

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint(self, sh, _):
        """ Test for basic simple linting functionality """
        sh.git.side_effect = ["6f29bf81a8322a04071bb794666e48c443a90360",
                              u"test åuthor\x00test-email@föo.com\x002016-12-03 15:28:15 01:00\x00åbc\n"
                              u"commït-title\n\ncommït-body",
                              u"file1.txt\npåth/to/file2.txt\n"]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli)
            self.assertEqual(stderr.getvalue(), u'3: B5 Body message is too short (11<20): "commït-body"\n')
            self.assertEqual(result.exit_code, 1)

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint_multiple_commits(self, sh, _):
        """ Test for --commits option """

        sh.git.side_effect = ["6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
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
                              u"file6.txt\npåth/to/file7.txt\n"]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar"])
            expected = (u"Commit 6f29bf81a8:\n"
                        u'3: B5 Body message is too short (12<20): "commït-body1"\n\n'
                        u"Commit 25053ccec5:\n"
                        u'3: B5 Body message is too short (12<20): "commït-body2"\n\n'
                        u"Commit 4da2656b0d:\n"
                        u'3: B5 Body message is too short (12<20): "commït-body3"\n')
            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 3)

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_lint_multiple_commits_config(self, sh, _):
        """ Test for --commits option where some of the commits have gitlint config in the commit message """

        # Note that the second commit title has a trailing period that is being ignored by gitlint-ignore: T3
        sh.git.side_effect = ["6f29bf81a8322a04071bb794666e48c443a90360\n" +  # git rev-list <SHA>
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
                              u"commït-title3\n\ncommït-body3",
                              u"file6.txt\npåth/to/file7.txt\n"]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--commits", "foo...bar"])
            # We expect that the second commit has no failures because of 'gitlint-ignore: T3' in its commit msg body
            expected = (u"Commit 6f29bf81a8:\n"
                        u'3: B5 Body message is too short (12<20): "commït-body1"\n\n'
                        u"Commit 4da2656b0d:\n"
                        u'3: B5 Body message is too short (12<20): "commït-body3"\n')
            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 2)

    @patch('gitlint.cli.stdin_has_data', return_value=True)
    def test_input_stream(self, _):
        """ Test for linting when a message is passed via stdin """
        expected_output = u"1: T2 Title has trailing whitespace: \"WIP: tïtle \"\n" + \
                          u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: tïtle \"\n" + \
                          u"3: B6 Body message is missing\n"

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, input=u'WIP: tïtle \n')
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

    @patch('gitlint.cli.stdin_has_data', return_value=True)
    def test_silent_mode(self, _):
        """ Test for --silent option """
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["--silent"], input=u"WIP: tïtle \n")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(result.exit_code, 3)
            self.assertEqual(result.output, "")

    @patch('gitlint.cli.stdin_has_data', return_value=True)
    def test_verbosity(self, _):
        """ Test for --verbosity option """
        # We only test -v and -vv, more testing is really not required here
        # -v
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            result = self.cli.invoke(cli.cli, ["-v"], input=u"WIP: tïtle \n")
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

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_debug(self, sh, _):
        """ Test for --debug option """

        sh.git.side_effect = ["6f29bf81a8322a04071bb794666e48c443a90360\n"  # git rev-list <SHA>
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
                              u"file6.txt\npåth/to/file7.txt\n"]

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            config_path = self.get_sample_path("config/gitlintconfig")
            result = self.cli.invoke(cli.cli, ["--config", config_path, "--debug", "--commits",
                                               "foo...bar"])

            expected = "Commit 6f29bf81a8:\n3: B5\n\n" + \
                       "Commit 25053ccec5:\n1: T3\n3: B5\n\n" + \
                       "Commit 4da2656b0d:\n2: B4\n3: B5\n3: B6\n"

            self.assertEqual(stderr.getvalue(), expected)
            self.assertEqual(result.exit_code, 6)

            # Make sure gitlint captured the correct logs
            expected_logs = [u"DEBUG: gitlint.cli Platform: {0}".format(platform.platform()),
                             u"DEBUG: gitlint.cli Python version: {0}".format(sys.version),
                             u"DEBUG: gitlint.cli Git version: git version 1.2.3",
                             u"DEBUG: gitlint.cli Gitlint version: {0}".format(__version__),
                             self.get_expected('debug_configuration_output1', {'config_path': config_path,
                                                                               'target': os.path.abspath(os.getcwd())}),
                             u"DEBUG: gitlint.lint Linting commit 6f29bf81a8322a04071bb794666e48c443a90360",
                             u"DEBUG: gitlint.lint Commit Object\nAuthor: test åuthor1 <test-email1@föo.com>\n" +
                             u"Date:   2016-12-03 15:28:15+01:00\ncommït-title1\n\ncommït-body1",
                             u"DEBUG: gitlint.lint Linting commit 25053ccec5e28e1bb8f7551fdbb5ab213ada2401",
                             u"DEBUG: gitlint.lint Commit Object\nAuthor: test åuthor2 <test-email2@föo.com>\n" +
                             u"Date:   2016-12-04 15:28:15+01:00\ncommït-title2.\n\ncommït-body2",
                             u"DEBUG: gitlint.lint Linting commit 4da2656b0dadc76c7ee3fd0243a96cb64007f125",
                             u"DEBUG: gitlint.lint Commit Object\nAuthor: test åuthor3 <test-email3@föo.com>\n" +
                             u"Date:   2016-12-05 15:28:15+01:00\nföo\nbar",
                             u"DEBUG: gitlint.cli Exit Code = 6"]

            self.assert_logged(expected_logs)

    @patch('gitlint.cli.stdin_has_data', return_value=True)
    def test_extra_path(self, _):
        """ Test for --extra-path flag """
        # Test extra-path pointing to a directory
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            extra_path = self.get_sample_path("user_rules")
            result = self.cli.invoke(cli.cli, ["--extra-path", extra_path, "--debug"], input=u"Test tïtle\n")
            expected_output = u"1: UC1 Commit violåtion 1: \"Contënt 1\"\n" + \
                              "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

        # Test extra-path pointing to a file
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            extra_path = self.get_sample_path("user_rules/my_commit_rules.py")
            result = self.cli.invoke(cli.cli, ["--extra-path", extra_path, "--debug"], input=u"Test tïtle\n")
            expected_output = u"1: UC1 Commit violåtion 1: \"Contënt 1\"\n" + \
                              "3: B6 Body message is missing\n"
            self.assertEqual(stderr.getvalue(), expected_output)
            self.assertEqual(result.exit_code, 2)

    @patch('gitlint.cli.stdin_has_data', return_value=True)
    def test_config_file(self, _):
        """ Test for --config option """
        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            config_path = self.get_sample_path("config/gitlintconfig")
            result = self.cli.invoke(cli.cli, ["--config", config_path], input=u"WIP: tëst")
            self.assertEqual(result.output, "")
            self.assertEqual(stderr.getvalue(), "1: T5\n3: B6\n")
            self.assertEqual(result.exit_code, 2)

    def test_config_file_negative(self):
        """ Negative test for --config option """
        # Directory as config file
        config_path = self.get_sample_path("config")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = u"Error: Invalid value for \"-C\" / \"--config\": Path \"{0}\" is a directory.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[2], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Non existing file
        config_path = self.get_sample_path(u"föo")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        expected_string = u"Error: Invalid value for \"-C\" / \"--config\": Path \"{0}\" does not exist.".format(
            config_path)
        self.assertEqual(result.output.split("\n")[2], expected_string)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)

        # Invalid config file
        config_path = self.get_sample_path("config/invalid-option-value")
        result = self.cli.invoke(cli.cli, ["--config", config_path])
        self.assertEqual(result.exit_code, self.CONFIG_ERROR_CODE)

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    def test_target(self, _):
        """ Test for the --target option """
        result = self.cli.invoke(cli.cli, ["--target", "/tmp"])
        # We expect gitlint to tell us that /tmp is not a git repo (this proves that it takes the target parameter
        # into account).
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        expected_path = os.path.realpath("/tmp")
        self.assertEqual(result.output, "%s is not a git repository.\n" % expected_path)

    def test_target_negative(self):
        """ Negative test for the --target option """
        # try setting a non-existing target
        result = self.cli.invoke(cli.cli, ["--target", u"/föo/bar"])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = u"Error: Invalid value for \"--target\": Directory \"/föo/bar\" does not exist."
        self.assertEqual(result.output.split("\n")[2], expected_msg)

        # try setting a file as target
        target_path = self.get_sample_path("config/gitlintconfig")
        result = self.cli.invoke(cli.cli, ["--target", target_path])
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = u"Error: Invalid value for \"--target\": Directory \"{0}\" is a file.".format(target_path)
        self.assertEqual(result.output.split("\n")[2], expected_msg)

    @patch('gitlint.config.LintConfigGenerator.generate_config')
    def test_generate_config(self, generate_config):
        """ Test for the generate-config subcommand """
        result = self.cli.invoke(cli.cli, ["generate-config"], input=u"tëstfile\n")
        self.assertEqual(result.exit_code, 0)
        expected_msg = u"Please specify a location for the sample gitlint config file [.gitlint]: tëstfile\n" + \
                       u"Successfully generated {0}\n".format(os.path.abspath(u"tëstfile"))
        self.assertEqual(result.output, expected_msg)
        generate_config.assert_called_once_with(os.path.abspath(u"tëstfile"))

    def test_generate_config_negative(self):
        """ Negative test for the generate-config subcommand """
        # Non-existing directory
        result = self.cli.invoke(cli.cli, ["generate-config"], input=u"/föo/bar")
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = u"Please specify a location for the sample gitlint config file [.gitlint]: /föo/bar\n" + \
                       u"Error: Directory '/föo' does not exist.\n"
        self.assertEqual(result.output, expected_msg)

        # Existing file
        sample_path = self.get_sample_path("config/gitlintconfig")
        result = self.cli.invoke(cli.cli, ["generate-config"], input=sample_path)
        self.assertEqual(result.exit_code, self.USAGE_ERROR_CODE)
        expected_msg = "Please specify a location for the sample gitlint " + \
                       "config file [.gitlint]: {0}\n".format(sample_path) + \
                       "Error: File \"{0}\" already exists.\n".format(sample_path)
        self.assertEqual(result.output, expected_msg)

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_git_error(self, sh, _):
        """ Tests that the cli handles git errors properly """
        sh.git.side_effect = CommandNotFound("git")
        result = self.cli.invoke(cli.cli)
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)

    @patch('gitlint.cli.stdin_has_data', return_value=False)
    @patch('gitlint.git.sh')
    def test_no_commits_in_range(self, sh, _):
        """ Test for --commits with the specified range being empty. """
        sh.git.side_effect = lambda *_args, **_kwargs: ""
        result = self.cli.invoke(cli.cli, ["--commits", "master...HEAD"])
        expected = u'No commits in range "master...HEAD".\n'
        self.assertEqual(result.output, expected)
        self.assertEqual(result.exit_code, 0)

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook')
    def test_install_hook(self, install_hook):
        """ Test for install-hook subcommand """
        result = self.cli.invoke(cli.cli, ["install-hook"])
        expected_path = os.path.join(os.getcwd(), hooks.COMMIT_MSG_HOOK_DST_PATH)
        expected = "Successfully installed gitlint commit-msg hook in {0}\n".format(expected_path)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        expected_config = config.LintConfig()
        expected_config.target = os.path.abspath(os.getcwd())
        install_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.install_commit_msg_hook')
    def test_install_hook_target(self, install_hook):
        """  Test for install-hook subcommand with a specific --target option specified """
        # Specified target
        result = self.cli.invoke(cli.cli, ["--target", self.SAMPLES_DIR, "install-hook"])
        expected_path = os.path.realpath(os.path.join(self.SAMPLES_DIR, hooks.COMMIT_MSG_HOOK_DST_PATH))
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
        expected_config.target = os.path.abspath(os.getcwd())
        install_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook')
    def test_uninstall_hook(self, uninstall_hook):
        """ Test for uninstall-hook subcommand """
        result = self.cli.invoke(cli.cli, ["uninstall-hook"])
        expected_path = os.path.realpath(os.path.join(os.getcwd(), hooks.COMMIT_MSG_HOOK_DST_PATH))
        expected = "Successfully uninstalled gitlint commit-msg hook from {0}\n".format(expected_path)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)
        expected_config = config.LintConfig()
        expected_config.target = os.path.abspath(os.getcwd())
        uninstall_hook.assert_called_once_with(expected_config)

    @patch('gitlint.hooks.GitHookInstaller.uninstall_commit_msg_hook', side_effect=hooks.GitHookInstallerError(u"tëst"))
    def test_uninstall_hook_negative(self, uninstall_hook):
        """ Negative test for uninstall-hook subcommand """
        result = self.cli.invoke(cli.cli, ["uninstall-hook"])
        self.assertEqual(result.exit_code, self.GIT_CONTEXT_ERROR_CODE)
        self.assertEqual(result.output, u"tëst\n")
        expected_config = config.LintConfig()
        expected_config.target = os.path.abspath(os.getcwd())
        uninstall_hook.assert_called_once_with(expected_config)
