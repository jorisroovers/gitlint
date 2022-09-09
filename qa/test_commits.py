# pylint: disable=too-many-function-args,unexpected-keyword-arg
import re

import arrow

from qa.shell import echo, git, gitlint
from qa.base import BaseTestCase


class CommitsTests(BaseTestCase):
    """Integration tests for the --commits argument, i.e. linting multiple commits or linting specific commits"""

    def test_successful(self):
        """Test linting multiple commits without violations"""
        git("checkout", "-b", "test-branch-commits-base", _cwd=self.tmp_git_repo)
        self.create_simple_commit("Sïmple title\n\nSimple bödy describing the commit")
        git("checkout", "-b", "test-branch-commits", _cwd=self.tmp_git_repo)
        self.create_simple_commit("Sïmple title2\n\nSimple bödy describing the commit2")
        self.create_simple_commit("Sïmple title3\n\nSimple bödy describing the commit3")
        output = gitlint(
            "--commits", "test-branch-commits-base...test-branch-commits", _cwd=self.tmp_git_repo, _tty_in=True
        )
        self.assertEqualStdout(output, "")

    def test_violations(self):
        """Test linting multiple commits with violations"""
        git("checkout", "-b", "test-branch-commits-violations-base", _cwd=self.tmp_git_repo)
        self.create_simple_commit("Sïmple title.\n")
        git("checkout", "-b", "test-branch-commits-violations", _cwd=self.tmp_git_repo)

        self.create_simple_commit("Sïmple title2.\n")
        commit_sha1 = self.get_last_commit_hash()[:10]
        self.create_simple_commit("Sïmple title3.\n")
        commit_sha2 = self.get_last_commit_hash()[:10]
        output = gitlint(
            "--commits",
            "test-branch-commits-violations-base...test-branch-commits-violations",
            _cwd=self.tmp_git_repo,
            _tty_in=True,
            _ok_code=[4],
        )

        self.assertEqual(output.exit_code, 4)
        expected_kwargs = {"commit_sha1": commit_sha1, "commit_sha2": commit_sha2}
        self.assertEqualStdout(output, self.get_expected("test_commits/test_violations_1", expected_kwargs))

    def test_csv_hash_list(self):
        """Test linting multiple commits (comma-separated) with violations"""
        git("checkout", "-b", "test-branch-commits-violations-base", _cwd=self.tmp_git_repo)
        self.create_simple_commit("Sïmple title1.\n")
        commit_sha1 = self.get_last_commit_hash()[:10]
        git("checkout", "-b", "test-branch-commits-violations", _cwd=self.tmp_git_repo)

        self.create_simple_commit("Sïmple title2.\n")
        commit_sha2 = self.get_last_commit_hash()[:10]
        self.create_simple_commit("Sïmple title3.\n")
        self.create_simple_commit("Sïmple title4.\n")
        commit_sha4 = self.get_last_commit_hash()[:10]

        # Lint subset of the commits in a specific order, passed in via csv list
        output = gitlint(
            "--commits",
            f"{commit_sha2},{commit_sha1},{commit_sha4}",
            _cwd=self.tmp_git_repo,
            _tty_in=True,
            _ok_code=[6],
        )

        self.assertEqual(output.exit_code, 6)
        expected_kwargs = {"commit_sha1": commit_sha1, "commit_sha2": commit_sha2, "commit_sha4": commit_sha4}
        self.assertEqualStdout(output, self.get_expected("test_commits/test_csv_hash_list_1", expected_kwargs))

    def test_lint_empty_commit_range(self):
        """Tests `gitlint --commits <sha>^...<sha>` --fail-without-commits where the provided range is empty."""
        self.create_simple_commit("Sïmple title.\n")
        self.create_simple_commit("Sïmple title2.\n")
        commit_sha = self.get_last_commit_hash()
        # git revspec -> 2 dots: <exclusive sha>..<inclusive sha> -> empty range when using same start and end sha
        refspec = f"{commit_sha}..{commit_sha}"

        # Regular gitlint invocation should run without issues
        output = gitlint("--commits", refspec, _cwd=self.tmp_git_repo, _tty_in=True)
        self.assertEqual(output.exit_code, 0)
        self.assertEqualStdout(output, "")

        # Gitlint should fail when --fail-without-commits is used
        output = gitlint(
            "--commits",
            refspec,
            "--fail-without-commits",
            _cwd=self.tmp_git_repo,
            _tty_in=True,
            _ok_code=[self.GITLINT_USAGE_ERROR],
        )
        self.assertEqual(output.exit_code, self.GITLINT_USAGE_ERROR)
        self.assertEqualStdout(output, f'Error: No commits in range "{refspec}"\n')

    def test_lint_single_commit(self):
        """Tests `gitlint --commits <sha>^...<same sha>`"""
        self.create_simple_commit("Sïmple title.\n")
        first_commit_sha = self.get_last_commit_hash()
        self.create_simple_commit("Sïmple title2.\n")
        commit_sha = self.get_last_commit_hash()
        refspec = f"{commit_sha}^...{commit_sha}"
        self.create_simple_commit("Sïmple title3.\n")

        expected = '1: T3 Title has trailing punctuation (.): "Sïmple title2."\n' + "3: B6 Body message is missing\n"

        # Lint using --commit <commit sha>
        output = gitlint("--commit", commit_sha, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        self.assertEqual(output.exit_code, 2)
        self.assertEqualStdout(output, expected)

        # Lint a single commit using --commits <refspec> pointing to the single commit
        output = gitlint("--commits", refspec, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        self.assertEqual(output.exit_code, 2)
        self.assertEqualStdout(output, expected)

        # Lint the first commit in the repository. This is a use-case that is not supported by --commits
        # As <sha>^...<sha> is not correct refspec in case <sha> points to the initial commit (which has no parents)
        expected = '1: T3 Title has trailing punctuation (.): "Sïmple title."\n' + "3: B6 Body message is missing\n"
        output = gitlint("--commit", first_commit_sha, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[2])
        self.assertEqual(output.exit_code, 2)
        self.assertEqualStdout(output, expected)

        # Assert that indeed --commits <refspec> is not supported when <refspec> points the the first commit
        refspec = f"{first_commit_sha}^...{first_commit_sha}"
        output = gitlint("--commits", refspec, _cwd=self.tmp_git_repo, _tty_in=True, _ok_code=[254])
        self.assertEqual(output.exit_code, 254)

    def test_lint_staged_stdin(self):
        """Tests linting a staged commit. Gitint should lint the passed commit message andfetch additional meta-data
        from the underlying repository. The easiest way to test this is by inspecting `--debug` output.
        This is the equivalent of doing:
        echo "WIP: Pïpe test." | gitlint --staged --debug
        """
        # Create a commit first, before we stage changes. This ensures the repo is properly initialized.
        self.create_simple_commit("Sïmple title.\n")

        # Add some files, stage them: they should show up in the debug output as changed file
        filename1 = self.create_file(self.tmp_git_repo)
        git("add", filename1, _cwd=self.tmp_git_repo)
        filename2 = self.create_file(self.tmp_git_repo)
        git("add", filename2, _cwd=self.tmp_git_repo)

        output = gitlint(
            echo("WIP: Pïpe test."),
            "--staged",
            "--debug",
            _cwd=self.tmp_git_repo,
            _tty_in=False,
            _err_to_out=True,
            _ok_code=[3],
        )

        # Determine variable parts of expected output
        expected_kwargs = self.get_debug_vars_last_commit()
        filenames = sorted([filename1, filename2])
        expected_kwargs.update(
            {
                "changed_files": filenames,
                "changed_files_stats": (
                    f"{filenames[0]}: 0 additions, 0 deletions\n  {filenames[1]}: 0 additions, 0 deletions"
                ),
            }
        )

        # It's not really possible to determine the "Date: ..." line that is part of the debug output as this date
        # is not taken from git but instead generated by gitlint itself. As a workaround, we extract the date from the
        # gitlint output using a regex, parse the date to ensure the format is correct, and then pass that as an
        # expected variable.
        matches = re.search(r"^Date:\s+(.*)", str(output), re.MULTILINE)
        if matches:
            expected_date = arrow.get(str(matches.group(1)), "YYYY-MM-DD HH:mm:ss Z").format("YYYY-MM-DD HH:mm:ss Z")
            expected_kwargs["staged_date"] = expected_date

        self.assertEqualStdout(output, self.get_expected("test_commits/test_lint_staged_stdin_1", expected_kwargs))
        self.assertEqual(output.exit_code, 3)

    def test_lint_staged_msg_filename(self):
        """Tests linting a staged commit. Gitint should lint the passed commit message andfetch additional meta-data
        from the underlying repository. The easiest way to test this is by inspecting `--debug` output.
        This is the equivalent of doing:
        gitlint --msg-filename /tmp/my-commit-msg --staged --debug
        """
        # Create a commit first, before we stage changes. This ensures the repo is properly initialized.
        self.create_simple_commit("Sïmple title.\n")

        # Add some files, stage them: they should show up in the debug output as changed file
        filename1 = self.create_file(self.tmp_git_repo)
        git("add", filename1, _cwd=self.tmp_git_repo)
        filename2 = self.create_file(self.tmp_git_repo)
        git("add", filename2, _cwd=self.tmp_git_repo)

        tmp_commit_msg_file = self.create_tmpfile("WIP: from fïle test.")

        output = gitlint(
            "--msg-filename",
            tmp_commit_msg_file,
            "--staged",
            "--debug",
            _cwd=self.tmp_git_repo,
            _tty_in=False,
            _err_to_out=True,
            _ok_code=[3],
        )

        # Determine variable parts of expected output
        expected_kwargs = self.get_debug_vars_last_commit()
        filenames = sorted([filename1, filename2])
        expected_kwargs.update(
            {
                "changed_files": filenames,
                "changed_files_stats": (
                    f"{filenames[0]}: 0 additions, 0 deletions\n  {filenames[1]}: 0 additions, 0 deletions"
                ),
            }
        )

        # It's not really possible to determine the "Date: ..." line that is part of the debug output as this date
        # is not taken from git but instead generated by gitlint itself. As a workaround, we extract the date from the
        # gitlint output using a regex, parse the date to ensure the format is correct, and then pass that as an
        # expected variable.
        matches = re.search(r"^Date:\s+(.*)", str(output), re.MULTILINE)
        if matches:
            expected_date = arrow.get(str(matches.group(1)), "YYYY-MM-DD HH:mm:ss Z").format("YYYY-MM-DD HH:mm:ss Z")
            expected_kwargs["staged_date"] = expected_date

        expected = self.get_expected("test_commits/test_lint_staged_msg_filename_1", expected_kwargs)
        self.assertEqualStdout(output, expected)
        self.assertEqual(output.exit_code, 3)

    def test_lint_head(self):
        """Testing whether we can also recognize special refs like 'HEAD'"""
        tmp_git_repo = self.create_tmp_git_repo()
        self.create_simple_commit("Sïmple title.\n\nSimple bödy describing the commit", git_repo=tmp_git_repo)
        self.create_simple_commit("Sïmple title", git_repo=tmp_git_repo)
        self.create_simple_commit("WIP: Sïmple title\n\nSimple bödy describing the commit", git_repo=tmp_git_repo)
        output = gitlint("--commits", "HEAD", _cwd=tmp_git_repo, _tty_in=True, _ok_code=[3])
        revlist = git("rev-list", "HEAD", _tty_in=True, _cwd=tmp_git_repo).split()

        expected_kwargs = {
            "commit_sha0": revlist[0][:10],
            "commit_sha1": revlist[1][:10],
            "commit_sha2": revlist[2][:10],
        }

        self.assertEqualStdout(output, self.get_expected("test_commits/test_lint_head_1", expected_kwargs))

    def test_ignore_commits(self):
        """Tests multiple commits of which some rules get ignored because of ignore-* rules"""
        # Create repo and some commits
        tmp_git_repo = self.create_tmp_git_repo()
        self.create_simple_commit("Sïmple title.\n\nSimple bödy describing the commit", git_repo=tmp_git_repo)
        # Normally, this commit will give T3 (trailing-punctuation), T5 (WIP) and B5 (bod-too-short) violations
        # But in this case only B5 because T3 and T5 are being ignored because of config
        self.create_simple_commit("Release: WIP tïtle.\n\nShort", git_repo=tmp_git_repo)
        # In the following 2 commits, the T3 violations are as normal
        self.create_simple_commit("Sïmple WIP title3.\n\nThis is \ta relëase commit\nMore info", git_repo=tmp_git_repo)
        self.create_simple_commit("Sïmple title4.\n\nSimple bödy describing the commit4", git_repo=tmp_git_repo)
        revlist = git("rev-list", "HEAD", _tty_in=True, _cwd=tmp_git_repo).split()

        config_path = self.get_sample_path("config/ignore-release-commits")
        output = gitlint("--commits", "HEAD", "--config", config_path, _cwd=tmp_git_repo, _tty_in=True, _ok_code=[4])

        expected_kwargs = {
            "commit_sha0": revlist[0][:10],
            "commit_sha1": revlist[1][:10],
            "commit_sha2": revlist[2][:10],
            "commit_sha3": revlist[3][:10],
        }
        self.assertEqualStdout(output, self.get_expected("test_commits/test_ignore_commits_1", expected_kwargs))
