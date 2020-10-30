# -*- coding: utf-8 -*-

from io import StringIO

from unittest.mock import patch  # pylint: disable=no-name-in-module, import-error

from gitlint.display import Display
from gitlint.config import LintConfig
from gitlint.tests.base import BaseTestCase


class DisplayTests(BaseTestCase):
    def test_v(self):
        display = Display(LintConfig())
        display.config.verbosity = 2

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            # Non exact outputting, should output both v and vv output
            with patch('gitlint.display.stdout', new=StringIO()) as stdout:
                display.v("tëst")
                display.vv("tëst2")
                # vvvv should be ignored regardless
                display.vvv("tëst3.1")
                display.vvv("tëst3.2", exact=True)
                self.assertEqual("tëst\ntëst2\n", stdout.getvalue())

            # exact outputting, should only output v
            with patch('gitlint.display.stdout', new=StringIO()) as stdout:
                display.v("tëst", exact=True)
                display.vv("tëst2", exact=True)
                # vvvv should be ignored regardless
                display.vvv("tëst3.1")
                display.vvv("tëst3.2", exact=True)
                self.assertEqual("tëst2\n", stdout.getvalue())

            # standard error should be empty throughtout all of this
            self.assertEqual('', stderr.getvalue())

    def test_e(self):
        display = Display(LintConfig())
        display.config.verbosity = 2

        with patch('gitlint.display.stdout', new=StringIO()) as stdout:
            # Non exact outputting, should output both v and vv output
            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                display.e("tëst")
                display.ee("tëst2")
                # vvvv should be ignored regardless
                display.eee("tëst3.1")
                display.eee("tëst3.2", exact=True)
                self.assertEqual("tëst\ntëst2\n", stderr.getvalue())

            # exact outputting, should only output v
            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                display.e("tëst", exact=True)
                display.ee("tëst2", exact=True)
                # vvvv should be ignored regardless
                display.eee("tëst3.1")
                display.eee("tëst3.2", exact=True)
                self.assertEqual("tëst2\n", stderr.getvalue())

            # standard output should be empty throughtout all of this
            self.assertEqual('', stdout.getvalue())
