---
title: User Defined Rules
---
# User Defined Rules
[:octicons-tag-24: v0.8.0][v0.8.0] 

Gitlint supports the concept of **user-defined** rules: the ability for users to write their own custom rules in python.

In a nutshell, set the `extra-path` configuration variable to point gitlint to a directory where it will search
for python files containing gitlint rule classes.

=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    extra-path=tools/gitlint/myrules # (1)

    # Alternatively, point to a specific file
    [general]
    extra-path=tools/gitlint/myrules/my_rules.py
    ```

    1. This path is relative to the current working directory in which you're executing gitlint.
        ```ini
        # You can also use absolute paths of course
        [general]
        extra-path=/opt/gitlint/my_rules.py
        ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --extra-path "tools/gitlint/myrules" # (1)
    # Alternatively, point to a specific file
    gitlint --extra-path "tools/gitlint/myrules/my_rules.py"
    
    # You can also use -c style config flags
    gitlint -c general.extra-path=tools/gitlint/myrules
    ```

    1. This path is relative to the current working directory in which you're executing gitlint.
        ```sh
        # You can also use absolute paths of course
        gitlint --extra-path "/opt/gitlint/my_rules.py"
        ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_EXTRA_PATH=tools/gitlint/myrules gitlint # (1)
    # Alternatively, point to a specific file
    GITLINT_EXTRA_PATH=tools/gitlint/myrules/my_rules.py gitlint
    ```

    1. This path is relative to the current working directory in which you're executing gitlint.
        ```sh
        # You can also use absolute paths of course
        GITLINT_EXTRA_PATH=/opt/gitlint/myrules gitlint
        ```

Example using the [`examples` directory in the gitlint source code](https://github.com/jorisroovers/gitlint/tree/main/examples):

```sh
$ cat examples/commit-message-1 | gitlint --extra-path examples/
1: UC2 Body does not contain a 'Signed-off-by Line' # (1)
```

1.  Example output of a user-defined **Signed-off-by** rule. Other violations occuring in
    [examples/commit-message-1](https://github.com/jorisroovers/gitlint/blob/main/examples/commit-message-1) were
    removed for brevity.


The `SignedOffBy` user-defined `CommitRule` was discovered by gitlint when it discovered
[examples/gitlint/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_commit_rules.py)

```{ .python .copy title="examples/my_commit_rules.py" linenums="1"}
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

    def validate(self, commit):
        log_msg = "This will be visible when running `gitlint --debug`"
        self.log.debug(log_msg)

        for line in commit.message.body:
            if line.startswith("Signed-off-by"):
                return

        msg = "Body does not contain a 'Signed-off-by' line"
        return [RuleViolation(self.id, msg, line_nr=1)]
```

If you want to check whether your rules are properly discovered by gitlint, you can use the `--debug` flag:

```sh
$ gitlint --debug --extra-path examples/
# [output cut for brevity]
  UC1: body-max-line-count
     body-max-line-count=3
  UC2: body-requires-signed-off-by
  UL1: title-no-special-chars
     special-chars=['$', '^', '%', '@', '!', '*', '(', ')']
```

!!! Tip
    In most cases it's really the easiest to just copy an example from the
    [examples](https://github.com/jorisroovers/gitlint/tree/main/examples) directory and modify it to your needs.
    The remainder of this page contains the technical details, mostly for reference.
