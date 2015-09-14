from gitlint.tests.base import BaseTestCase


class GitTests(BaseTestCase):
    def test_get_latest_commit(self):
        # Some issues with mocking out the 'sh' library. Need to investigate this further.
        pass
