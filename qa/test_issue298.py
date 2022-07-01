from qa.base import BaseTestCase
from qa.shell import gitlint

class Issue298(BaseTestCase):


    def test_issue298(self):
        output = gitlint("issue298")
        self.assertEqualStdout(output, "gitlint: \x1b[31mThis is a test\x1b[0m\n")
        