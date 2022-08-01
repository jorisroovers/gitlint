import re

from gitlint.options import ListOption
from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation

RULE_REGEX = re.compile(r"(.*)users\.noreply\.github\.com(.*)")


class BlockGithubAuthor(CommitRule):
    """ This rule enforces that no github author information (email address) is
    used for committing
    """

    name = "contrib-block-github-author"
    id = "BG1"

    def validate(self, line, commit):
        if commit.is_merge_commit:
            # We do not care about merge-commits here
            return []

        if commit.author_email is None:
            return [RuleViolation(self.id, f"No author information in commit", line)]
        else:
            match = RULE_REGEX.match(commit.author_email)

            if not match:
                # All good
                return []

            return [RuleViolation(self.id, f"GitHub email address found in commit author information", line)]

