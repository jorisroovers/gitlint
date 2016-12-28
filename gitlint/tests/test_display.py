# -*- coding: utf-8 -*-

try:
    # python 2.x
    from StringIO import StringIO
except ImportError:
    # python 3.x
    from io import StringIO

from mock import patch

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
                display.v(u"tëst")
                display.vv(u"tëst2")
                # vvvv should be ignored regardless
                display.vvv(u"tëst3.1")
                display.vvv(u"tëst3.2", exact=True)
                self.assertEqual(u"tëst\ntëst2\n", stdout.getvalue())

            # exact outputting, should only output v
            with patch('gitlint.display.stdout', new=StringIO()) as stdout:
                display.v(u"tëst", exact=True)
                display.vv(u"tëst2", exact=True)
                # vvvv should be ignored regardless
                display.vvv(u"tëst3.1")
                display.vvv(u"tëst3.2", exact=True)
                self.assertEqual(u"tëst2\n", stdout.getvalue())

            # standard error should be empty throughtout all of this
            self.assertEqual('', stderr.getvalue())

    def test_e(self):
        display = Display(LintConfig())
        display.config.verbosity = 2

        with patch('gitlint.display.stdout', new=StringIO()) as stdout:
            # Non exact outputting, should output both v and vv output
            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                display.e(u"tëst")
                display.ee(u"tëst2")
                # vvvv should be ignored regardless
                display.eee(u"tëst3.1")
                display.eee(u"tëst3.2", exact=True)
                self.assertEqual(u"tëst\ntëst2\n", stderr.getvalue())

            # exact outputting, should only output v
            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                display.e(u"tëst", exact=True)
                display.ee(u"tëst2", exact=True)
                # vvvv should be ignored regardless
                display.eee(u"tëst3.1")
                display.eee(u"tëst3.2", exact=True)
                self.assertEqual(u"tëst2\n", stderr.getvalue())

            # standard output should be empty throughtout all of this
            self.assertEqual('', stdout.getvalue())
