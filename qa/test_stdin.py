# -*- coding: utf-8 -*-
import subprocess
from sh import gitlint, echo  # pylint: disable=no-name-in-module
from qa.base import BaseTestCase, ustr


class StdInTests(BaseTestCase):
    """ Integration tests for various STDIN scenarios for gitlint """

    def test_stdin_pipe(self):
        """ Test piping input into gitlint.
            This is the equivalent of doing:
            $ echo "foo" | gitlint
        """
        # NOTE: There is no use in testing this with _tty_in=True, because if you pipe something into a command
        # there never is a TTY connected to stdin (per definition). We're setting _tty_in=False here to be explicit
        # but note that this is always true when piping something into a command.
        output = gitlint(echo(u"WIP: Pïpe test."), _tty_in=False, _err_to_out=True, _ok_code=[3])

        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: Pïpe test.\"\n" + \
                   u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: Pïpe test.\"\n" + \
                   u"3: B6 Body message is missing\n"

        self.assertEqual(output, expected)

    def test_stdin_pipe_empty(self):
        """ Test the scenario where no TTY is attached an nothing is piped into gitlint. This occurs in
            CI runners like Jenkins and Gitlab, see https://github.com/jorisroovers/gitlint/issues/42 for details.
            This is the equivalent of doing:
            $ echo -n "" | gitlint
        """
        commit_msg = u"WIP: This ïs a title.\nContent on the sëcond line"
        self._create_simple_commit(commit_msg)

        # We need to set _err_to_out explicitly for sh to merge stdout and stderr output in case there's
        # no TTY attached to STDIN
        # http://amoffat.github.io/sh/sections/special_arguments.html?highlight=_tty_in#err-to-out
        output = gitlint(_cwd=self.tmp_git_repo, _in=self.mock_stdin(), _tty_in=False, _err_to_out=True, _ok_code=[3])

        expected = u"1: T3 Title has trailing punctuation (.): \"WIP: This ïs a title.\"\n" + \
            u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: This ïs a title.\"\n" + \
            u"2: B4 Second line is not empty: \"Content on the sëcond line\"\n"
        self.assertEqual(output, expected)

    def test_stdin_file(self):
        """ Test the scenario where STDIN is a regular file (stat.S_ISREG = True)
            This is the equivalent of doing:
            $ gitlint < myfile
        """
        tmp_commit_msg_file = self.create_tmpfile("WIP: STDIN ïs a file test.")

        with open(tmp_commit_msg_file) as file_handle:

            # We need to use subprocess.Popen() here instead of sh because when passing a file_handle to sh, it will
            # deal with reading the file itself instead of passing it on to gitlint as a STDIN. Since we're trying to
            # test for the condition where stat.S_ISREG == True that won't work for us here.
            p = subprocess.Popen(u"gitlint", stdin=file_handle, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, _ = p.communicate()

            expected = u"1: T3 Title has trailing punctuation (.): \"WIP: STDIN ïs a file test.\"\n" + \
                       u"1: T5 Title contains the word 'WIP' (case-insensitive): \"WIP: STDIN ïs a file test.\"\n" + \
                       u"3: B6 Body message is missing\n"
            self.assertEqual(ustr(output), expected)
