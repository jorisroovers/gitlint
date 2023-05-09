## Quick start
```sh
# Install gitlint
pip install gitlint # (1)

# Check the last commit message
gitlint
# Lint all commits in your repo
gitlint --commits HEAD # (2)
# Lint specific single commit
gitlint --commit abc123

# Read the commit-msg from a file
gitlint --msg-filename examples/commit-message-2
# Pipe a commit message to gitlint
git log -1 --pretty=%B | gitlint

# Install gitlint commit-msg hook
gitlint install-hook # (3)
```

1. See [Installation](installation.md) for all available packages and supported package managers.
2. Any [refspec or comma separated list of commit hashes](linting_specific_commits.md) will work.
3. You can also [use pre-commit](commit_hooks.md#pre-commit).

Output example:
```sh
$ cat examples/commit-message-2 | gitlint
1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T4 Title contains hard tab characters (\t): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
2: B4 Second line is not empty: "This line should not contain text"
3: B1 Line exceeds max length (125>80): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B2 Line has trailing whitespace: "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B3 Line contains hard tab characters (\t): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
```
!!! note
    The returned exit code equals the number of errors found. [Some exit codes are special](exit_codes.md).

## Configuration

Gitlint can be configured via a ` .gitlint` file, CLI or environment variables - a short sample is provided below.

For in-depth documentation of general and rule-specific configuration options, refer to the [Configuration](configuration/index.md) and [Rules](rules/index.md) documentation.

=== ":octicons-file-code-16:  .gitlint"

    ```ini title=".gitlint"
    [general]
    # Ignore rules, reference them by id or name (comma-separated)
    ignore=title-trailing-punctuation, T3

    # Enable specific community contributed rules
    contrib=contrib-title-conventional-commits,CC1

    # Set the extra-path where gitlint will search for user defined rules
    extra-path=./gitlint_rules/my_rules.py

    ### Configuring rules ### (1)

    [title-max-length]
    line-length=80 

    [title-min-length]
    min-length=5
    ```

    1.  Rules and sections can be referenced by their full name or by id. For example, the rule
        `[title-max-length]` could also be referenced as `[T1]`.
        ```ini
        [T1]
        line-length=80
        ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    # Change gitlint's verbosity.
    $ gitlint -v
    # Ignore certain rules
    $ gitlint --ignore body-is-missing,T3
    # Enable debug mode
    $ gitlint --debug
    # Load user-defined rules
    $ gitlint --extra-path /home/joe/mygitlint_rules
    # Set any config option using -c
    $ gitlint -c general.verbosity=2 -c title-max-length.line-length=80
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    # Change gitlint's verbosity.
    $ GITLINT_VERBOSITY=1 gitlint
    # Ignore certain rules
    $ GITLINT_IGNORE="body-is-missing,T3" gitlint
    # Enable debug mode
    $ GITLINT_DEBUG=1 --debug
    # Load user-defined rules
    $ GITLINT_EXTRA_PATH="/home/joe/mygitlint_rules" gitlint
    ```