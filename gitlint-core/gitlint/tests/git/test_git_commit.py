import copy
import datetime

import dateutil

import arrow

from unittest.mock import patch, call

from gitlint.tests.base import BaseTestCase
from gitlint.git import GitContext, GitCommit, GitContextError, LocalGitCommit, StagedLocalGitCommit, GitCommitMessage
from gitlint.shell import ErrorReturnCode


class GitCommitTests(BaseTestCase):
    # Expected special_args passed to 'sh'
    expected_sh_special_args = {"_tty_out": False, "_cwd": "fåke/path"}

    @patch("gitlint.git.sh")
    def test_get_latest_commit(self, sh):
        sample_sha = "d8ac47e9f2923c7f22d8668e3a1ed04eb4cdbca9"

        sh.git.side_effect = [
            sample_sha,
            "test åuthor\x00test-emåil@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\ncömmit-title\n\ncömmit-body",
            "#",  # git config --get core.commentchar
            "file1.txt\npåth/to/file2.txt\n",
            "foöbar\n* hürdur\n",
        ]

        context = GitContext.from_local_repository("fåke/path")
        # assert that commit info was read using git command
        expected_calls = [
            call("log", "-1", "--pretty=%H", **self.expected_sh_special_args),
            call("log", sample_sha, "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--root",
                sample_sha,
                **self.expected_sh_special_args,
            ),
            call("branch", "--contains", sample_sha, **self.expected_sh_special_args),
        ]

        # Only first 'git log' call should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:1])

        last_commit = context.commits[-1]
        self.assertIsInstance(last_commit, LocalGitCommit)
        self.assertEqual(last_commit.sha, sample_sha)
        self.assertEqual(last_commit.message.title, "cömmit-title")
        self.assertEqual(last_commit.message.body, ["", "cömmit-body"])
        self.assertEqual(last_commit.author_name, "test åuthor")
        self.assertEqual(last_commit.author_email, "test-emåil@foo.com")
        self.assertEqual(
            last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
        )
        self.assertListEqual(last_commit.parents, ["åbc"])
        self.assertFalse(last_commit.is_merge_commit)
        self.assertFalse(last_commit.is_fixup_commit)
        self.assertFalse(last_commit.is_fixup_amend_commit)
        self.assertFalse(last_commit.is_squash_commit)
        self.assertFalse(last_commit.is_revert_commit)

        # First 2 'git log' calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:3])

        self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])
        # 'git diff-tree' should have happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:4])

        self.assertListEqual(last_commit.branches, ["foöbar", "hürdur"])
        # All expected calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls)

    @patch("gitlint.git.sh")
    def test_from_local_repository_specific_refspec(self, sh):
        sample_refspec = "åbc123..def456"
        sample_sha = "åbc123"

        sh.git.side_effect = [
            sample_sha,  # git rev-list <sample_refspec>
            "test åuthor\x00test-emåil@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\ncömmit-title\n\ncömmit-body",
            "#",  # git config --get core.commentchar
            "file1.txt\npåth/to/file2.txt\n",
            "foöbar\n* hürdur\n",
        ]

        context = GitContext.from_local_repository("fåke/path", refspec=sample_refspec)
        # assert that commit info was read using git command
        expected_calls = [
            call("rev-list", sample_refspec, **self.expected_sh_special_args),
            call("log", sample_sha, "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--root",
                sample_sha,
                **self.expected_sh_special_args,
            ),
            call("branch", "--contains", sample_sha, **self.expected_sh_special_args),
        ]

        # Only first 'git log' call should've happened at this point
        self.assertEqual(sh.git.mock_calls, expected_calls[:1])

        last_commit = context.commits[-1]
        self.assertIsInstance(last_commit, LocalGitCommit)
        self.assertEqual(last_commit.sha, sample_sha)
        self.assertEqual(last_commit.message.title, "cömmit-title")
        self.assertEqual(last_commit.message.body, ["", "cömmit-body"])
        self.assertEqual(last_commit.author_name, "test åuthor")
        self.assertEqual(last_commit.author_email, "test-emåil@foo.com")
        self.assertEqual(
            last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
        )
        self.assertListEqual(last_commit.parents, ["åbc"])
        self.assertFalse(last_commit.is_merge_commit)
        self.assertFalse(last_commit.is_fixup_commit)
        self.assertFalse(last_commit.is_fixup_amend_commit)
        self.assertFalse(last_commit.is_squash_commit)
        self.assertFalse(last_commit.is_revert_commit)

        # First 2 'git log' calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:3])

        self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])
        # 'git diff-tree' should have happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:4])

        self.assertListEqual(last_commit.branches, ["foöbar", "hürdur"])
        # All expected calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls)

    @patch("gitlint.git.sh")
    def test_from_local_repository_specific_commit_hash(self, sh):
        sample_hash = "åbc123"

        sh.git.side_effect = [
            sample_hash,  # git log -1 <sample_hash>
            "test åuthor\x00test-emåil@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\ncömmit-title\n\ncömmit-body",
            "#",  # git config --get core.commentchar
            "file1.txt\npåth/to/file2.txt\n",
            "foöbar\n* hürdur\n",
        ]

        context = GitContext.from_local_repository("fåke/path", commit_hashes=[sample_hash])
        # assert that commit info was read using git command
        expected_calls = [
            call("log", "-1", sample_hash, "--pretty=%H", **self.expected_sh_special_args),
            call("log", sample_hash, "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--root",
                sample_hash,
                **self.expected_sh_special_args,
            ),
            call("branch", "--contains", sample_hash, **self.expected_sh_special_args),
        ]

        # Only first 'git log' call should've happened at this point
        self.assertEqual(sh.git.mock_calls, expected_calls[:1])

        last_commit = context.commits[-1]
        self.assertIsInstance(last_commit, LocalGitCommit)
        self.assertEqual(last_commit.sha, sample_hash)
        self.assertEqual(last_commit.message.title, "cömmit-title")
        self.assertEqual(last_commit.message.body, ["", "cömmit-body"])
        self.assertEqual(last_commit.author_name, "test åuthor")
        self.assertEqual(last_commit.author_email, "test-emåil@foo.com")
        self.assertEqual(
            last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
        )
        self.assertListEqual(last_commit.parents, ["åbc"])
        self.assertFalse(last_commit.is_merge_commit)
        self.assertFalse(last_commit.is_fixup_commit)
        self.assertFalse(last_commit.is_fixup_amend_commit)
        self.assertFalse(last_commit.is_squash_commit)
        self.assertFalse(last_commit.is_revert_commit)

        # First 2 'git log' calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:3])

        self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])
        # 'git diff-tree' should have happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:4])

        self.assertListEqual(last_commit.branches, ["foöbar", "hürdur"])
        # All expected calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls)

    @patch("gitlint.git.sh")
    def test_from_local_repository_multiple_commit_hashes(self, sh):
        hashes = ["åbc123", "dęf456", "ghí789"]
        sh.git.side_effect = [
            *hashes,
            f"test åuthor {hashes[0]}\x00test-emåil-{hashes[0]}@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            f"cömmit-title {hashes[0]}\n\ncömmit-body {hashes[0]}",
            "#",  # git config --get core.commentchar
            f"test åuthor {hashes[1]}\x00test-emåil-{hashes[1]}@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            f"cömmit-title {hashes[1]}\n\ncömmit-body {hashes[1]}",
            f"test åuthor {hashes[2]}\x00test-emåil-{hashes[2]}@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
            f"cömmit-title {hashes[2]}\n\ncömmit-body {hashes[2]}",
            f"file1-{hashes[0]}.txt\npåth/to/file2.txt\n",
            f"file1-{hashes[1]}.txt\npåth/to/file2.txt\n",
            f"file1-{hashes[2]}.txt\npåth/to/file2.txt\n",
            f"foöbar-{hashes[0]}\n* hürdur\n",
            f"foöbar-{hashes[1]}\n* hürdur\n",
            f"foöbar-{hashes[2]}\n* hürdur\n",
        ]

        expected_calls = [
            call("log", "-1", hashes[0], "--pretty=%H", **self.expected_sh_special_args),
            call("log", "-1", hashes[1], "--pretty=%H", **self.expected_sh_special_args),
            call("log", "-1", hashes[2], "--pretty=%H", **self.expected_sh_special_args),
            call("log", hashes[0], "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call("log", hashes[1], "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call("log", hashes[2], "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call(
                "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", hashes[0], **self.expected_sh_special_args
            ),
            call(
                "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", hashes[1], **self.expected_sh_special_args
            ),
            call(
                "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", hashes[2], **self.expected_sh_special_args
            ),
            call("branch", "--contains", hashes[0], **self.expected_sh_special_args),
            call("branch", "--contains", hashes[1], **self.expected_sh_special_args),
            call("branch", "--contains", hashes[2], **self.expected_sh_special_args),
        ]

        context = GitContext.from_local_repository("fåke/path", commit_hashes=hashes)

        # Only first set of 'git log' calls should've happened at this point
        self.assertEqual(sh.git.mock_calls, expected_calls[:3])

        for i, commit in enumerate(context.commits):
            expected_hash = hashes[i]
            self.assertIsInstance(commit, LocalGitCommit)
            self.assertEqual(commit.sha, expected_hash)
            self.assertEqual(commit.message.title, f"cömmit-title {expected_hash}")
            self.assertEqual(commit.message.body, ["", f"cömmit-body {expected_hash}"])
            self.assertEqual(commit.author_name, f"test åuthor {expected_hash}")
            self.assertEqual(commit.author_email, f"test-emåil-{expected_hash}@foo.com")
            self.assertEqual(
                commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
            )
            self.assertListEqual(commit.parents, ["åbc"])
            self.assertFalse(commit.is_merge_commit)
            self.assertFalse(commit.is_fixup_commit)
            self.assertFalse(commit.is_fixup_amend_commit)
            self.assertFalse(commit.is_squash_commit)
            self.assertFalse(commit.is_revert_commit)

        # All 'git log' calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:7])

        for i, commit in enumerate(context.commits):
            expected_hash = hashes[i]
            self.assertListEqual(commit.changed_files, [f"file1-{expected_hash}.txt", "påth/to/file2.txt"])

        # 'git diff-tree' should have happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:10])

        for i, commit in enumerate(context.commits):
            expected_hash = hashes[i]
            self.assertListEqual(commit.branches, [f"foöbar-{expected_hash}", "hürdur"])

        # All expected calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls)

    @patch("gitlint.git.sh")
    def test_get_latest_commit_merge_commit(self, sh):
        sample_sha = "d8ac47e9f2923c7f22d8668e3a1ed04eb4cdbca9"

        sh.git.side_effect = [
            sample_sha,
            'test åuthor\x00test-emåil@foo.com\x002016-12-03 15:28:15 +0100\x00åbc def\nMerge "foo bår commit"',
            "#",  # git config --get core.commentchar
            "file1.txt\npåth/to/file2.txt\n",
            "foöbar\n* hürdur\n",
        ]

        context = GitContext.from_local_repository("fåke/path")
        # assert that commit info was read using git command
        expected_calls = [
            call("log", "-1", "--pretty=%H", **self.expected_sh_special_args),
            call("log", sample_sha, "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--root",
                sample_sha,
                **self.expected_sh_special_args,
            ),
            call("branch", "--contains", sample_sha, **self.expected_sh_special_args),
        ]

        # Only first 'git log' call should've happened at this point
        self.assertEqual(sh.git.mock_calls, expected_calls[:1])

        last_commit = context.commits[-1]
        self.assertIsInstance(last_commit, LocalGitCommit)
        self.assertEqual(last_commit.sha, sample_sha)
        self.assertEqual(last_commit.message.title, 'Merge "foo bår commit"')
        self.assertEqual(last_commit.message.body, [])
        self.assertEqual(last_commit.author_name, "test åuthor")
        self.assertEqual(last_commit.author_email, "test-emåil@foo.com")
        self.assertEqual(
            last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
        )
        self.assertListEqual(last_commit.parents, ["åbc", "def"])
        self.assertTrue(last_commit.is_merge_commit)
        self.assertFalse(last_commit.is_fixup_commit)
        self.assertFalse(last_commit.is_fixup_amend_commit)
        self.assertFalse(last_commit.is_squash_commit)
        self.assertFalse(last_commit.is_revert_commit)

        # First 2 'git log' calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:3])

        self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])
        # 'git diff-tree' should have happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[:4])

        self.assertListEqual(last_commit.branches, ["foöbar", "hürdur"])
        # All expected calls should've happened at this point
        self.assertListEqual(sh.git.mock_calls, expected_calls)

    @patch("gitlint.git.sh")
    def test_get_latest_commit_fixup_squash_commit(self, sh):
        commit_prefixes = {"fixup": "is_fixup_commit", "squash": "is_squash_commit", "amend": "is_fixup_amend_commit"}
        for commit_type in commit_prefixes.keys():
            sample_sha = "d8ac47e9f2923c7f22d8668e3a1ed04eb4cdbca9"

            sh.git.side_effect = [
                sample_sha,
                "test åuthor\x00test-emåil@foo.com\x002016-12-03 15:28:15 +0100\x00åbc\n"
                f'{commit_type}! "foo bår commit"',
                "#",  # git config --get core.commentchar
                "file1.txt\npåth/to/file2.txt\n",
                "foöbar\n* hürdur\n",
            ]

            context = GitContext.from_local_repository("fåke/path")
            # assert that commit info was read using git command
            expected_calls = [
                call("log", "-1", "--pretty=%H", **self.expected_sh_special_args),
                call("log", sample_sha, "-1", "--pretty=%aN%x00%aE%x00%ai%x00%P%n%B", **self.expected_sh_special_args),
                call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
                call(
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    "--root",
                    sample_sha,
                    **self.expected_sh_special_args,
                ),
                call("branch", "--contains", sample_sha, **self.expected_sh_special_args),
            ]

            # Only first 'git log' call should've happened at this point
            self.assertEqual(sh.git.mock_calls, expected_calls[:-4])

            last_commit = context.commits[-1]
            self.assertIsInstance(last_commit, LocalGitCommit)
            self.assertEqual(last_commit.sha, sample_sha)
            self.assertEqual(last_commit.message.title, f'{commit_type}! "foo bår commit"')
            self.assertEqual(last_commit.message.body, [])
            self.assertEqual(last_commit.author_name, "test åuthor")
            self.assertEqual(last_commit.author_email, "test-emåil@foo.com")
            self.assertEqual(
                last_commit.date, datetime.datetime(2016, 12, 3, 15, 28, 15, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
            )
            self.assertListEqual(last_commit.parents, ["åbc"])

            # First 2 'git log' calls should've happened at this point
            self.assertEqual(sh.git.mock_calls, expected_calls[:3])

            # Asserting that squash and fixup are correct
            for type, attr in commit_prefixes.items():
                self.assertEqual(getattr(last_commit, attr), commit_type == type)

            self.assertFalse(last_commit.is_merge_commit)
            self.assertFalse(last_commit.is_revert_commit)
            self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])

            self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])
            # 'git diff-tree' should have happened at this point
            self.assertListEqual(sh.git.mock_calls, expected_calls[:4])

            self.assertListEqual(last_commit.branches, ["foöbar", "hürdur"])
            # All expected calls should've happened at this point
            self.assertListEqual(sh.git.mock_calls, expected_calls)

            sh.git.reset_mock()

    @patch("gitlint.git.git_commentchar")
    def test_from_commit_msg_full(self, commentchar):
        commentchar.return_value = "#"
        gitcontext = GitContext.from_commit_msg(self.get_sample("commit_message/sample1"))

        expected_title = "Commit title contåining 'WIP', as well as trailing punctuation."
        expected_body = [
            "This line should be empty",
            "This is the first line of the commit message body and it is meant to test a "
            + "line that exceeds the maximum line length of 80 characters.",
            "This line has a tråiling space. ",
            "This line has a trailing tab.\t",
        ]
        expected_full = expected_title + "\n" + "\n".join(expected_body)
        expected_original = (
            expected_full + "\n# This is a cömmented  line\n"
            "# ------------------------ >8 ------------------------\n"
            "# Anything after this line should be cleaned up\n"
            "# this line appears on `git commit -v` command\n"
            "diff --git a/gitlint/tests/samples/commit_message/sample1 "
            "b/gitlint/tests/samples/commit_message/sample1\n"
            "index 82dbe7f..ae71a14 100644\n"
            "--- a/gitlint/tests/samples/commit_message/sample1\n"
            "+++ b/gitlint/tests/samples/commit_message/sample1\n"
            "@@ -1 +1 @@\n"
        )

        commit = gitcontext.commits[-1]
        self.assertIsInstance(commit, GitCommit)
        self.assertFalse(isinstance(commit, LocalGitCommit))
        self.assertEqual(commit.message.title, expected_title)
        self.assertEqual(commit.message.body, expected_body)
        self.assertEqual(commit.message.full, expected_full)
        self.assertEqual(commit.message.original, expected_original)
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertListEqual(commit.branches, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertFalse(commit.is_fixup_commit)
        self.assertFalse(commit.is_fixup_amend_commit)
        self.assertFalse(commit.is_squash_commit)
        self.assertFalse(commit.is_revert_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_just_title(self):
        gitcontext = GitContext.from_commit_msg(self.get_sample("commit_message/sample2"))
        commit = gitcontext.commits[-1]

        self.assertIsInstance(commit, GitCommit)
        self.assertFalse(isinstance(commit, LocalGitCommit))
        self.assertEqual(commit.message.title, "Just a title contåining WIP")
        self.assertEqual(commit.message.body, [])
        self.assertEqual(commit.message.full, "Just a title contåining WIP")
        self.assertEqual(commit.message.original, "Just a title contåining WIP")
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertListEqual(commit.parents, [])
        self.assertListEqual(commit.branches, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertFalse(commit.is_fixup_commit)
        self.assertFalse(commit.is_fixup_amend_commit)
        self.assertFalse(commit.is_squash_commit)
        self.assertFalse(commit.is_revert_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_empty(self):
        gitcontext = GitContext.from_commit_msg("")
        commit = gitcontext.commits[-1]

        self.assertIsInstance(commit, GitCommit)
        self.assertFalse(isinstance(commit, LocalGitCommit))
        self.assertEqual(commit.message.title, "")
        self.assertEqual(commit.message.body, [])
        self.assertEqual(commit.message.full, "")
        self.assertEqual(commit.message.original, "")
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertListEqual(commit.branches, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertFalse(commit.is_fixup_commit)
        self.assertFalse(commit.is_fixup_amend_commit)
        self.assertFalse(commit.is_squash_commit)
        self.assertFalse(commit.is_revert_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    @patch("gitlint.git.git_commentchar")
    def test_from_commit_msg_comment(self, commentchar):
        commentchar.return_value = "#"
        gitcontext = GitContext.from_commit_msg("Tïtle\n\nBödy 1\n#Cömment\nBody 2")
        commit = gitcontext.commits[-1]

        self.assertIsInstance(commit, GitCommit)
        self.assertFalse(isinstance(commit, LocalGitCommit))
        self.assertEqual(commit.message.title, "Tïtle")
        self.assertEqual(commit.message.body, ["", "Bödy 1", "Body 2"])
        self.assertEqual(commit.message.full, "Tïtle\n\nBödy 1\nBody 2")
        self.assertEqual(commit.message.original, "Tïtle\n\nBödy 1\n#Cömment\nBody 2")
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertListEqual(commit.branches, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertFalse(commit.is_fixup_commit)
        self.assertFalse(commit.is_squash_commit)
        self.assertFalse(commit.is_fixup_amend_commit)
        self.assertFalse(commit.is_revert_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_merge_commit(self):
        commit_msg = "Merge f919b8f34898d9b48048bcd703bc47139f4ff621 into 8b0409a26da6ba8a47c1fd2e746872a8dab15401"
        gitcontext = GitContext.from_commit_msg(commit_msg)
        commit = gitcontext.commits[-1]

        self.assertIsInstance(commit, GitCommit)
        self.assertFalse(isinstance(commit, LocalGitCommit))
        self.assertEqual(commit.message.title, commit_msg)
        self.assertEqual(commit.message.body, [])
        self.assertEqual(commit.message.full, commit_msg)
        self.assertEqual(commit.message.original, commit_msg)
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertListEqual(commit.branches, [])
        self.assertTrue(commit.is_merge_commit)
        self.assertFalse(commit.is_fixup_commit)
        self.assertFalse(commit.is_fixup_amend_commit)
        self.assertFalse(commit.is_squash_commit)
        self.assertFalse(commit.is_revert_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_revert_commit(self):
        commit_msg = 'Revert "Prev commit message"\n\nThis reverts commit a8ad67e04164a537198dea94a4fde81c5592ae9c.'
        gitcontext = GitContext.from_commit_msg(commit_msg)
        commit = gitcontext.commits[-1]

        self.assertIsInstance(commit, GitCommit)
        self.assertFalse(isinstance(commit, LocalGitCommit))
        self.assertEqual(commit.message.title, 'Revert "Prev commit message"')
        self.assertEqual(commit.message.body, ["", "This reverts commit a8ad67e04164a537198dea94a4fde81c5592ae9c."])
        self.assertEqual(commit.message.full, commit_msg)
        self.assertEqual(commit.message.original, commit_msg)
        self.assertEqual(commit.author_name, None)
        self.assertEqual(commit.author_email, None)
        self.assertEqual(commit.date, None)
        self.assertListEqual(commit.parents, [])
        self.assertListEqual(commit.branches, [])
        self.assertFalse(commit.is_merge_commit)
        self.assertFalse(commit.is_fixup_commit)
        self.assertFalse(commit.is_fixup_amend_commit)
        self.assertFalse(commit.is_squash_commit)
        self.assertTrue(commit.is_revert_commit)
        self.assertEqual(len(gitcontext.commits), 1)

    def test_from_commit_msg_fixup_squash_amend_commit(self):
        # mapping between cleanup commit prefixes and the commit object attribute
        commit_prefixes = {"fixup": "is_fixup_commit", "squash": "is_squash_commit", "amend": "is_fixup_amend_commit"}

        for commit_type in commit_prefixes.keys():
            commit_msg = f"{commit_type}! Test message"
            gitcontext = GitContext.from_commit_msg(commit_msg)
            commit = gitcontext.commits[-1]

            self.assertIsInstance(commit, GitCommit)
            self.assertFalse(isinstance(commit, LocalGitCommit))
            self.assertEqual(commit.message.title, commit_msg)
            self.assertEqual(commit.message.body, [])
            self.assertEqual(commit.message.full, commit_msg)
            self.assertEqual(commit.message.original, commit_msg)
            self.assertEqual(commit.author_name, None)
            self.assertEqual(commit.author_email, None)
            self.assertEqual(commit.date, None)
            self.assertListEqual(commit.parents, [])
            self.assertListEqual(commit.branches, [])
            self.assertEqual(len(gitcontext.commits), 1)
            self.assertFalse(commit.is_merge_commit)
            self.assertFalse(commit.is_revert_commit)
            # Asserting that squash and fixup are correct
            for type, commit_attr_name in commit_prefixes.items():
                self.assertEqual(getattr(commit, commit_attr_name), commit_type == type)

    @patch("gitlint.git.sh")
    @patch("arrow.now")
    def test_staged_commit(self, now, sh):
        # StagedLocalGitCommit()

        sh.git.side_effect = [
            "#",  # git config --get core.commentchar
            "test åuthor\n",  # git config --get user.name
            "test-emåil@foo.com\n",  # git config --get user.email
            "my-brånch\n",  # git rev-parse --abbrev-ref HEAD
            "file1.txt\npåth/to/file2.txt\n",
        ]
        now.side_effect = [arrow.get("2020-02-19T12:18:46.675182+01:00")]

        # We use a fixup commit, just to test a non-default path
        context = GitContext.from_staged_commit("fixup! Foōbar 123\n\ncömmit-body\n", "fåke/path")

        # git calls we're expecting
        expected_calls = [
            call("config", "--get", "core.commentchar", _ok_code=[0, 1], **self.expected_sh_special_args),
            call("config", "--get", "user.name", **self.expected_sh_special_args),
            call("config", "--get", "user.email", **self.expected_sh_special_args),
            call("rev-parse", "--abbrev-ref", "HEAD", **self.expected_sh_special_args),
            call("diff", "--staged", "--name-only", "-r", **self.expected_sh_special_args),
        ]

        last_commit = context.commits[-1]
        self.assertIsInstance(last_commit, StagedLocalGitCommit)
        self.assertIsNone(last_commit.sha, None)
        self.assertEqual(last_commit.message.title, "fixup! Foōbar 123")
        self.assertEqual(last_commit.message.body, ["", "cömmit-body"])
        # Only `git config --get core.commentchar` should've happened up until this point
        self.assertListEqual(sh.git.mock_calls, expected_calls[0:1])

        self.assertEqual(last_commit.author_name, "test åuthor")
        self.assertListEqual(sh.git.mock_calls, expected_calls[0:2])

        self.assertEqual(last_commit.author_email, "test-emåil@foo.com")
        self.assertListEqual(sh.git.mock_calls, expected_calls[0:3])

        self.assertEqual(
            last_commit.date, datetime.datetime(2020, 2, 19, 12, 18, 46, tzinfo=dateutil.tz.tzoffset("+0100", 3600))
        )
        now.assert_called_once()

        self.assertListEqual(last_commit.parents, [])
        self.assertFalse(last_commit.is_merge_commit)
        self.assertTrue(last_commit.is_fixup_commit)
        self.assertFalse(last_commit.is_fixup_amend_commit)
        self.assertFalse(last_commit.is_squash_commit)
        self.assertFalse(last_commit.is_revert_commit)

        self.assertListEqual(last_commit.branches, ["my-brånch"])
        self.assertListEqual(sh.git.mock_calls, expected_calls[0:4])

        self.assertListEqual(last_commit.changed_files, ["file1.txt", "påth/to/file2.txt"])
        self.assertListEqual(sh.git.mock_calls, expected_calls[0:5])

    @patch("gitlint.git.sh")
    def test_staged_commit_with_missing_username(self, sh):
        # StagedLocalGitCommit()

        sh.git.side_effect = [
            "#",  # git config --get core.commentchar
            ErrorReturnCode("git config --get user.name", b"", b""),
        ]

        expected_msg = "Missing git configuration: please set user.name"
        with self.assertRaisesMessage(GitContextError, expected_msg):
            ctx = GitContext.from_staged_commit("Foōbar 123\n\ncömmit-body\n", "fåke/path")
            [str(commit) for commit in ctx.commits]

    @patch("gitlint.git.sh")
    def test_staged_commit_with_missing_email(self, sh):
        # StagedLocalGitCommit()

        sh.git.side_effect = [
            "#",  # git config --get core.commentchar
            "test åuthor\n",  # git config --get user.name
            ErrorReturnCode("git config --get user.name", b"", b""),
        ]

        expected_msg = "Missing git configuration: please set user.email"
        with self.assertRaisesMessage(GitContextError, expected_msg):
            ctx = GitContext.from_staged_commit("Foōbar 123\n\ncömmit-body\n", "fåke/path")
            [str(commit) for commit in ctx.commits]

    def test_gitcommitmessage_equality(self):
        commit_message1 = GitCommitMessage(GitContext(), "tëst\n\nfoo", "tëst\n\nfoo", "tēst", ["", "föo"])
        attrs = ["original", "full", "title", "body"]
        self.object_equality_test(commit_message1, attrs, {"context": commit_message1.context})

    @patch("gitlint.git._git")
    def test_gitcommit_equality(self, git):
        # git will be called to setup the context (commentchar and current_branch), just return the same value
        # This only matters to test gitcontext equality, not gitcommit equality
        git.return_value = "foöbar"

        # Test simple equality case
        now = datetime.datetime.utcnow()
        context1 = GitContext()
        commit_message1 = GitCommitMessage(context1, "tëst\n\nfoo", "tëst\n\nfoo", "tēst", ["", "föo"])
        commit1 = GitCommit(
            context1,
            commit_message1,
            "shä",
            now,
            "Jöhn Smith",
            "jöhn.smith@test.com",
            None,
            ["föo/bar"],
            ["brånch1", "brånch2"],
        )
        context1.commits = [commit1]

        context2 = GitContext()
        commit_message2 = GitCommitMessage(context2, "tëst\n\nfoo", "tëst\n\nfoo", "tēst", ["", "föo"])
        commit2 = GitCommit(
            context2,
            commit_message1,
            "shä",
            now,
            "Jöhn Smith",
            "jöhn.smith@test.com",
            None,
            ["föo/bar"],
            ["brånch1", "brånch2"],
        )
        context2.commits = [commit2]

        self.assertEqual(context1, context2)
        self.assertEqual(commit_message1, commit_message2)
        self.assertEqual(commit1, commit2)

        # Check that objects are unequal when changing a single attribute
        kwargs = {
            "message": commit1.message,
            "sha": commit1.sha,
            "date": commit1.date,
            "author_name": commit1.author_name,
            "author_email": commit1.author_email,
            "parents": commit1.parents,
            "changed_files": commit1.changed_files,
            "branches": commit1.branches,
        }

        self.object_equality_test(commit1, kwargs.keys(), {"context": commit1.context})

        # Check that the is_* attributes that are affected by the commit message affect equality
        special_messages = {
            "is_merge_commit": "Merge: foöbar",
            "is_fixup_commit": "fixup! foöbar",
            "is_squash_commit": "squash! foöbar",
            "is_revert_commit": "Revert: foöbar",
        }
        for key in special_messages:
            kwargs_copy = copy.deepcopy(kwargs)
            clone1 = GitCommit(context=commit1.context, **kwargs_copy)
            clone1.message = GitCommitMessage.from_full_message(context1, special_messages[key])
            self.assertTrue(getattr(clone1, key))

            clone2 = GitCommit(context=commit1.context, **kwargs_copy)
            clone2.message = GitCommitMessage.from_full_message(context1, "foöbar")
            self.assertNotEqual(clone1, clone2)

    @patch("gitlint.git.git_commentchar")
    def test_commit_msg_custom_commentchar(self, patched):
        patched.return_value = "ä"
        context = GitContext()
        message = GitCommitMessage.from_full_message(context, "Tïtle\n\nBödy 1\näCömment\nBody 2")

        self.assertEqual(message.title, "Tïtle")
        self.assertEqual(message.body, ["", "Bödy 1", "Body 2"])
        self.assertEqual(message.full, "Tïtle\n\nBödy 1\nBody 2")
        self.assertEqual(message.original, "Tïtle\n\nBödy 1\näCömment\nBody 2")
