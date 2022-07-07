from qa.base import BaseTestCase
from qa.shell import gitlint, git

class Issue298(BaseTestCase):


    def setUp(self):
        super().setUp()
        self.responses = []
        self.response_index = 0
        self.githook_output = []
        gitlint("install-hook", _cwd=self.tmp_git_repo)

    def _interact(self, line, stdin):
        self.githook_output.append(line)
        # Answer 'yes' to question to keep violating commit-msg
        if "Your commit message contains violations" in line:
            response = self.responses[self.response_index]
            stdin.put(f"{response}\n")
            self.response_index = (self.response_index + 1) % len(self.responses)

    def test_issue298(self):
        output = gitlint("issue298")
        self.assertEqualStdout(output, "gitlint: \x1b[31mThis is a test\x1b[0m\n")

    def test_issue298_no_tty(self):
        from sh import gitlint as mygitlint
        output = mygitlint("issue298")
        self.assertEqualStdout(output, "gitlint: \x1b[31mThis is a test\x1b[0m\n")

    def test_commit(self):
        self.create_simple_commit("This ïs a title\n\nBody contënt that should work",
                                                  out=self._interact, tty_in=True)
        print(self.githook_output)
        # breakpoint()
        self.assertEqual("gitlint: \x1b[31mThis is a test\x1b[0m\n", self.githook_output[1])