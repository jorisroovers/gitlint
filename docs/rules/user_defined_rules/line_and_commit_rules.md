[:octicons-tag-24: v0.8.0][v0.8.0] 

Gitlint has 2 types of user-defined rules for linting commit messages:

- `CommitRule`: applied once per commit
- `LineRule`: applied on a line-by line basis (targeting either the commit message title or every line in the commit message body).

The benefit of a `CommitRule` is that it allows for more complex checks that span multiple lines and/or checks
that should only be done once per commit. Conversely a `LineRule` allows for greater code re-use and implementation simplicity.

While every `LineRule` can be implemented as a `CommitRule`, the opposite is not true.

### Examples

In terms of code, writing your own `CommitRule` or `LineRule` is very similar.
The only 2 differences between a `CommitRule` and a `LineRule` are the parameters of the `validate(...)` method and the extra
`target` attribute that `LineRule` requires.

Consider the following `CommitRule` that can be found in [examples/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_commit_rules.py):

```{ .python .copy title="examples/my_commit_rules.py" linenums="1" hl_lines="16"}
from gitlint.rules import CommitRule, RuleViolation

class SignedOffBy(CommitRule):
    """Enforce that each commit contains a "Signed-off-by" line.
    We keep things simple here and just check whether the commit body
    contains a line that starts with "Signed-off-by".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id
    # We recommend starting with UC (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit): # (1)
        log_msg = "This will be visible when running `gitlint --debug`"
        self.log.debug(log_msg)

        for line in commit.message.body:
            if line.startswith("Signed-off-by"):
                return

        msg = "Body does not contain a 'Signed-off-by' line"
        return [RuleViolation(self.id, msg, line_nr=1)]
```

1. When extending from `CommitRule`, `validate(...)` takes a single [`commit` argument](#commit-object).

Contrast this with the following `LineRule` that can be found in [examples/my_line_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_line_rules.py):

```{ .python .copy title="examples/my_line_rules.py" linenums="1" hl_lines="17 28"}
from gitlint.rules import LineRule, RuleViolation, CommitMessageTitle
from gitlint.options import ListOption

class SpecialChars(LineRule):
    """This rule will enforce that the commit message title does not
    contain any of the following characters: $^%@!*()
    """

    # A rule MUST have a human friendly name
    name = "title-no-special-chars"

    # A rule MUST have a *unique* id.
    # We recommend starting with UL (for User-defined Line-rule)
    id = "UL1"

    # A line-rule MUST have a target (not required for CommitRules).
    target = CommitMessageTitle # (1)

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [
        ListOption(
            "special-chars", # option name
            ["$", "^", "%", "@", "!", "*", "(", ")"], # default value
            "Comma separated list of chars that cannot occur in the title",
        )
    ]

    def validate(self, line, _commit): # (2)
        self.log.debug("This will be visible when running `gitlint --debug`")

        violations = []
        # Options can be accessed by name lookup in self.options
        for char in self.options["special-chars"].value:
            if char in line:
                msg = f"Title contains the special character '{char}'"
                violation = RuleViolation(self.id, msg, line)
                violations.append(violation)

        return violations
```

1. In this example, we set to `target = CommitMessageTitle`  indicating that this `LineRule`
   should only be applied once to the commit message title. <br><br>
   The alternative value for `target` is `CommitMessageBody`,
   in which case gitlint will apply your rule to **every** line in the commit message body.
2. When extending from `LineRule`, `validate(...)` get the `line` against which they are applied as the first argument and
   the [`commit` object](#commit-object) of which the line is part of as second.

You might also noticed the extra `options_spec` class attribute which allows you to make your rules configurable.
[Options](options.md) are not unique to `LineRule`s, they can also be used by `CommitRule`s.


## Commit object
Both `CommitRule`s and `LineRule`s take a `commit` object in their `validate(...)` methods.
The table below outlines the various attributes of that commit object that can be used during validation.


| Property                                       | Type                                       | Description                                                                          |
| ---------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------ |
| `commit`                                       | `#!python GitCommit`                       | Python object representing the commit                                                |
| `commit.message`                               | `#!python GitCommitMessage`                | Python object representing the commit message                                        |
| `commit.message.original`                      | `#!python str`                             | Original commit message as returned by git                                           |
| `commit.message.full`                          | `#!python str`                             | Full commit message, without comments (lines starting with `#` removed).             |
| `commit.message.title`                         | `#!python str`                             | Title/subject of the commit message: the first line                                  |
| `commit.message.body`                          | `#!python str[]`                           | List of lines in the body of the commit message (i.e. starting from the second line) |
| `commit.author_name`                           | `s#!python tr`                             | Name of the author, result of `git log --pretty=%aN`                                 |
| `commit.author_email`                          | `#!python str`                             | Email of the author, result of `git log --pretty=%aE`                                |
| `commit.date`                                  | `#!python datetime.datetime`               | Python `datetime` object representing the time of commit                             |
| `commit.is_merge_commit`                       | `#!python bool`                            | Boolean indicating whether the commit is a merge commit or not.                      |
| `commit.is_revert_commit`                      | `#!python bool`                            | Boolean indicating whether the commit is a revert commit or not.                     |
| `commit.is_fixup_commit`                       | `#!python bool`                            | Boolean indicating whether the commit is a fixup commit or not.                      |
| `commit.is_fixup_amend_commit`                 | `#!python bool`                            | Boolean indicating whether the commit is a (fixup) amend commit or not.              |
| `commit.is_squash_commit`                      | `#!python bool`                            | Boolean indicating whether the commit is a squash cosmmit or not.                    |
| `commit.parents`                               | `#!python str[]`                           | List of parent commit `sha`s (only for merge commits).                               |
| `commit.changed_files`                         | `#!python str[]`                           | List of files changed in the commit (relative paths).                                |
| `commit.changed_files_stats`                   | `#!python dict[str, GitChangedFilesStats]` | Dictionary mapping the changed files to a `GitChangedFilesStats` objects             |
| `#!python commit.changed_files_stats["a/b.txt"].filepath`  | `#!python pathlib.Path`                    | Relative path (compared to repo root) of the file that was changed.                  |
| `#!python commit.changed_files_stats["a/b.txt"].additions` | `#!python int`                             | Number of additions in the file.                                                     |
| `#!python commit.changed_files_stats["a/b.txt"].deletions` | `#!python int`                             | Number of deletions in the file.                                                     |
| `commit.branches`                              | `#!python str[]`                           | List of branch names the commit is part of                                           |
| `commit.context`                               | `#!python GitContext`                      | Object pointing to the bigger git context that the commit is part of                 |
| `commit.context.current_branch`                | `#!python str`                             | Name of the currently active branch (of local repo)                                  |
| `commit.context.repository_path`               | `#!python str`                             | Absolute path pointing to the git repository being linted                            |
| `commit.context.commits`                       | `#!python GitCommit[]`                     | List of commits gitlint is acting on, NOT all commits in the repo.                   |