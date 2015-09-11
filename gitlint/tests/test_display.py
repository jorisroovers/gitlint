from gitlint.display import Display
from gitlint.config import LintConfig
from gitlint.tests.base import BaseTestCase

from StringIO import StringIO
from mock import patch


class DisplayTests(BaseTestCase):
    def test_v(self):
        display = Display(LintConfig())
        display.config.verbosity = 2

        with patch('gitlint.display.stderr', new=StringIO()) as stderr:
            # Non exact outputting, should output both v and vv output
            with patch('gitlint.display.stdout', new=StringIO()) as stdout:
                display.v("test")
                display.vv("test2")
                self.assertEqual("test\ntest2\n", stdout.getvalue())

            # exact outputting, should only output v
            with patch('gitlint.display.stdout', new=StringIO()) as stdout:
                display.v("test", exact=True)
                display.vv("test2", exact=True)
                self.assertEqual("test2\n", stdout.getvalue())

            # standard error should be empty throughtout all of this
            self.assertEqual('', stderr.getvalue())

    def test_e(self):
        display = Display(LintConfig())
        display.config.verbosity = 2

        with patch('gitlint.display.stdout', new=StringIO()) as stdout:
            # Non exact outputting, should output both v and vv output
            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                display.e("test")
                display.ee("test2")
                self.assertEqual("test\ntest2\n", stderr.getvalue())

            # exact outputting, should only output v
            with patch('gitlint.display.stderr', new=StringIO()) as stderr:
                display.e("test", exact=True)
                display.ee("test2", exact=True)
                self.assertEqual("test2\n", stderr.getvalue())

            # standard error should be empty throughtout all of this
            self.assertEqual('', stdout.getvalue())
