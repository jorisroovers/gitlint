Gitlint has a number of options that modify it's overall behavior, documented below.

## silent
[:octicons-tag-24: v0.1.0][v0.1.0]

Enable silent mode (no output). Use [exit](index.md#exit-codes) code to determine result.

| Default value    | Type            | CLI flag   | Env var          |
| ---------------- | --------------- | ---------- | ---------------- |
| `#!python false` | `#!python bool` | `--silent` | `GITLINT_SILENT` |


=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --silent
    ```

=== ":material-application-variable-outline: Env var"
    
    ```sh
    GITLINT_SILENT=1 gitlint 
    ```

## verbosity
[:octicons-tag-24: v0.1.0][v0.1.0]

Amount of output gitlint will show when printing errors.

| Default value | Type           | CLI flag            | Env var             |
| ------------- | -------------- | ------------------- | ------------------- |
| `#!python 3`  | `#!python int` | `-v`, `-vv`, `-vvv` | `GITLINT_VERBOSITY` |



=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    verbosity=2
    ```

=== ":octicons-terminal-16: CLI"

    ```sh
    gitlint -vvv                   # default     (level 3)
    gitlint -vv                    # less output (level 2)
    gitlint -v                     # even less   (level 1)
    gitlint --silent               # no output   (level 0)
    gitlint -c general.verbosity=1 # Set specific level
    gitlint -c general.verbosity=0 # Same as --silent
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_VERBOSITY=2 gitlint   
    ```


## ignore
[:octicons-tag-24: v0.1.0][v0.1.0]

Comma separated list of rules to ignore (by name or id).

| Default value              | Type            | CLI flag   | Env var          |
| -------------------------- | --------------- | ---------- | ---------------- |
| `#!python []` (empty list) | `#!python list` | `--ignore` | `GITLINT_IGNORE` |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    ignore=T1,body-min-length
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --ignore=body-min-length              # ignore single rule
    gitlint --ignore=T1,body-min-length           # ignore multiple rule
    gitlint -c general.ignore=T1,body-min-length  # different way of doing the same
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_IGNORE=T1,body-min-length gitlint
    ```



## debug
[:octicons-tag-24: v0.7.1][v0.7.1]

Enable debugging output.

| Default value    | Type            | CLI flag  | Env var         |
| ---------------- | --------------- | --------- | --------------- |
| `#!python false` | `#!python bool` | `--debug` | `GITLINT_DEBUG` |


=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --debug
    # --debug is special, the following does NOT work
    # gitlint -c general.debug=true
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_DEBUG=1 gitlint
    ```


## target
[:octicons-tag-24: v0.8.0][v0.8.0]

Target git repository gitlint should be linting against.

| Default value           | Type          | CLI flag | Env var    |
| ----------------------- | ------------- | -------- | ---------- |
| `#!python None` (empty) | `#!python str`    | `--target` | `GITLINT_TARGET` |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    target=/home/joe/myrepo/
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --target=/home/joe/myrepo/
    gitlint -c general.target=/home/joe/myrepo/  # different way of doing the same
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_TARGET=/home/joe/myrepo/ gitlint
    ```


## commit
[:octicons-tag-24: v0.16.0][v0.16.0]

Git reference of specific commit to lint.

| Default value | Type           | CLI flag   | Env var          |
| ------------- | -------------- | ---------- | ---------------- |
| `(empty)`     | `#!python str` | `--commit` | `GITLINT_COMMIT` |


=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --commit 019cf40580a471a3958d3c346aa8bfd265fe5e16
    gitlint --commit 019cf40  # short SHAs work too
    gitlint --commit HEAD~2   # as do special references
    gitlint --commit mybranch # lint latest commit on a branch 
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_COMMIT=019cf40580a471a3958d3c346aa8bfd265fe5e16 gitlint
    GITLINT_COMMIT=019cf40 gitlint  # short SHAs work too
    GITLINT_COMMIT=HEAD~2 gitlint   # as do special references
    GITLINT_COMMIT=mybranch gitlint # lint latest commit on a branch 
    ```

## commits
[:octicons-tag-24: v0.8.1][v0.8.1]

Range of commits (refspec or comma-separated hashes) to lint.

| Default value     | Type           | CLI flag    | Env var           |
| ----------------- | -------------- | ----------- | ----------------- |
| `#!python "HEAD"` | `#!python str` | `--commits` | `GITLINT_COMMITS` |


=== ":octicons-terminal-16:  CLI"

    ```sh
    # Lint a specific commit range
    gitlint --commits "019cf40...d6bc75a"
    # Lint all commits on a branch
    gitlint --commits mybranch
    # Lint all commits that are different between a branch and your main branch
    gitlint --commits "main..mybranch"
    # Use git's special references
    gitlint --commits "origin/main..HEAD"

    # You can also pass multiple, comma separated commit hashes
    gitlint --commits 019cf40,c50eb150,d6bc75a
    # These can include special references as well
    gitlint --commits HEAD~1,mybranch-name,origin/main,d6bc75a
    # You can also lint a single commit by adding a trailing comma
    gitlint --commits 019cf40,
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    # Lint a specific commit range
    GITLINT_COMMITS="019cf40...d6bc75a" gitlint
    # Lint all commits on a branch
    GITLINT_COMMITS=mybranch gitlint
    # Lint all commits that are different between a branch and your main branch
    GITLINT_COMMITS="main..mybranch" gitlint
    # Use git's special references
    GITLINT_COMMITS="origin/main..HEAD" gitlint

    # You can also pass multiple, comma separated commit hashes
    GITLINT_COMMITS=019cf40,c50eb150,d6bc75a gitlint
    # These can include special references as well
    GITLINT_COMMITS=HEAD~1,mybranch-name,origin/main,d6bc75a gitlint
    # You can also lint a single commit by adding a trailing comma
    GITLINT_COMMITS=019cf40, gitlint
    ```

## config
[:octicons-tag-24: v0.1.0][v0.1.0]

Path where gitlint looks for a config file.

| Default value         | Type           | CLI flag   | Env var          |
| --------------------- | -------------- | ---------- | ---------------- |
| `#!python ".gitlint"` | `#!python str` | `--config` | `GITLINT_CONFIG` |


=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --config=/home/joe/gitlint.ini
    gitlint -C /home/joe/gitlint.ini      # different way of doing the same
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_CONFIG=/home/joe/gitlint.ini 
    ```


## extra-path
[:octicons-tag-24: v0.8.0][v0.8.0]

Path where gitlint looks for [user-defined rules](../rules/user_defined_rules/getting_started.md).

| Default value          | Type          | CLI flag | Env var        |
| ---------------------- | ------------- | -------- | -------------- |
| `#!python None`(empty) | `#!python str`    | `--extra-path` | `GITLINT_EXTRA_PATH` |



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

## contrib
[:octicons-tag-24: v0.12.0][v0.12.0]

Comma-separated list of [Contrib rules](../rules/contrib_rules.md) to enable (by name or id).

| Default value           | Type          | CLI flag | Env var     |
| ----------------------- | ------------- | -------- | ----------- |
| `#!python None` (empty) | `#!python str`    | `--contrib` | `GITLINT_CONTRIB` |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    contrib=contrib-title-conventional-commits,CC1
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --contrib=contrib-title-conventional-commits,CC1
    # different way of doing the same
    gitlint -c general.contrib=contrib-title-conventional-commits,CC1
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_CONTRIB=contrib-title-conventional-commits,CC1 gitlint
    ```

## msg-filename
[:octicons-tag-24: v0.8.0][v0.8.0]

Path to a file containing the commit-msg to be linted.

| Default value           | Type          | CLI flag | Env var          |
| ----------------------- | ------------- | -------- | ---------------- |
| `#!python None` (empty) | `#!python str`    | `--msg-filename` | Not Available |



=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --msg-filename=/home/joe/mycommit-msg.txt
    ```

## staged
[:octicons-tag-24: v0.13.0][v0.13.0]

Attempt smart guesses about meta info (like author name, email, branch, changed files, etc) when manually passing a
commit message to gitlint via stdin or `--commit-msg`.

Since in such cases no actual git commit exists (yet) for the message being linted, gitlint
needs to apply some heuristics (like checking `git config` and any staged changes) to make a smart guess about what the
likely author name, email, commit date, changed files and branch of the ensuing commit would be.

When not using the `--staged` flag while linting a commit message via stdin or `--commit-msg`, gitlint will only have
access to the commit message itself for linting and won't be able to enforce rules like
[M1:author-valid-email](../rules/builtin_rules.md#m1-author-valid-email).

| Default value    | Type            | CLI flag   | Env var          |
| ---------------- | --------------- | ---------- | ---------------- |
| `#!python false` | `#!python bool` | `--staged` | `GITLINT_STAGED` |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    staged=true
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint --staged
    gitlint -c general.staged=true # different way of doing the same
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_STAGED=1 gitlint      
    ```


## fail-without-commits
[:octicons-tag-24: v0.16.0][v0.16.0]


Hard fail when the target commit range is empty. Note that gitlint will
already fail by default on invalid commit ranges. This option is specifically
to tell gitlint to fail on **valid but empty** commit ranges.

| Default value    | Type            | CLI flag                 | Env var                        |
| ---------------- | --------------- | ------------------------ | ------------------------------ |
| `#!python false` | `#!python bool` | `--fail-without-commits` | `GITLINT_FAIL_WITHOUT_COMMITS` |


=== ":octicons-file-code-16:  .gitlint"
    
    ```ini
    [general]
    fail-without-commits=true
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    # The following will cause gitlint to hard fail (i.e. exit code > 0)
    # since HEAD..HEAD is a valid but empty commit range.
    gitlint --fail-without-commits --commits HEAD..HEAD
    ```

=== ":material-application-variable-outline: Env var"

    ```sh
    GITLINT_FAIL_WITHOUT_COMMITS=1 gitlint      
    ```


## regex-style-search
[:octicons-tag-24: v0.18.0][v0.18.0]

Whether to use Python `re.search()` instead of `re.match()` semantics in all built-in rules that use regular expressions. 

??? "More context on **regex-style-search**"

    Python offers [two different primitive operations based on regular expressions](https://docs.python.org/3/library/re.html#search-vs-match): 
    `re.match()` checks for a match only at the beginning of the string, while `re.search()` checks for a match anywhere
    in the string.



    Most rules in gitlint already use `re.search()` instead of `re.match()`, but there's a few notable exceptions that
    use `re.match()`, which can lead to unexpected matching behavior.

    - M1 - author-valid-email
    - I1 - ignore-by-title
    - I2 - ignore-by-body
    - I3 - ignore-body-lines
    - I4 - ignore-by-author-name

    The `regex-style-search` option is meant to fix this inconsistency. Setting it to `true` will force the above rules to
    use `re.search()` instead of `re.match()`. For detailed context, see [issue #254](https://github.com/jorisroovers/gitlint/issues/254).

| Default value    | Type            | CLI flag                                | Env var       |
| ---------------- | --------------- | --------------------------------------- | ------------- |
| `#!python false` | `#!python bool` | `-c general.regex-style-search=<value>` | Not Available |

!!! important
    At this time, `regex-style-search` is **disabled** by default, but it will be **enabled** by default in the future.
    


Gitlint will log a warning when you're using a rule that uses a custom regex and this option is not enabled:

```plain
WARNING: I1 - ignore-by-title: gitlint will be switching from using Python regex 'match' (match beginning) to
'search' (match anywhere) semantics. Please review your ignore-by-title.regex option accordingly.
To remove this warning, set general.regex-style-search=True. 
More details: https://jorisroovers.github.io/gitlint/configuration/#regex-style-search
```

**If you don't use custom regexes, gitlint will not log a warning and no action is needed.**

**To remove the warning:** 

1. Review your regex in the rules gitlint warned for and ensure it's still accurate when using [`re.search()` semantics](https://docs.python.org/3/library/re.html#search-vs-match).
2. Enable `regex-style-search` in your gitlint config:

    === ":octicons-file-code-16:  .gitlint"

        ```ini
        [general]
        regex-style-search=true
        ```

    === ":octicons-terminal-16:  CLI"

        ```sh
        gitlint -c general.regex-style-search=true
        ```

## ignore-stdin
[:octicons-tag-24: v0.12.0][v0.12.0]

Ignore any stdin data. Sometimes useful when running gitlint in a CI server.

| Default value    | Type            | CLI flag         | Env var                |
| ---------------- | --------------- | ---------------- | ---------------------- |
| `#!python false` | `#!python bool` | `--ignore-stdin` | `GITLINT_IGNORE_STDIN` |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    ignore-stdin=true
    ```

=== ":octicons-terminal-16:  CLI"
    
    ```sh
    gitlint --ignore-stdin
    gitlint -c general.ignore-stdin=true # different way of doing the same
    ```

=== ":material-application-variable-outline: Env var"
    
    ```sh
    GITLINT_IGNORE_STDIN=1 gitlint      
    ```


## ignore-merge-commits
[:octicons-tag-24: v0.7.0][v0.7.0]

Whether or not to ignore merge commits.

| Default value   | Type            | CLI flag                                  | Env var       |
| --------------- | --------------- | ----------------------------------------- | ------------- |
| `#!python true` | `#!python bool` | `-c general.ignore-merge-commits=<value>` | Not Available |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    ignore-merge-commits=false
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint -c general.ignore-merge-commits=false
    ```


## ignore-revert-commits
[:octicons-tag-24: v0.13.0][v0.13.0]

Whether or not to ignore revert commits.

| Default value   | Type            | CLI flag                                   | Env var       |
| --------------- | --------------- | ------------------------------------------ | ------------- |
| `#!python true` | `#!python bool` | `-c general.ignore-revert-commits=<value>` | Not Available |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    ignore-revert-commits=false
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint -c general.ignore-revert-commits=false
    ```


## ignore-fixup-commits
[:octicons-tag-24: v0.9.0][v0.9.0]

Whether or not to ignore [fixup](https://git-scm.com/docs/git-commit#git-commit---fixupltcommitgt) commits.

| Default value   | Type            | CLI flag                                  | Env var       |
| --------------- | --------------- | ----------------------------------------- | ------------- |
| `#!python true` | `#!python bool` | `-c general.ignore-fixup-commits=<value>` | Not Available |



=== ":octicons-file-code-16:  .gitlint"
    
    ```ini
    [general]
    ignore-fixup-commits=false
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint -c general.ignore-fixup-commits=false
    ```


## ignore-fixup-amend-commits
[:octicons-tag-24: v0.18.0][v0.18.0]

Whether or not to ignore [fixup=amend](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---fixupamendrewordltcommitgt) commits.

| Default value   | Type            | CLI flag                                        | Env var       |
| --------------- | --------------- | ----------------------------------------------- | ------------- |
| `#!python true` | `#!python bool` | `-c general.ignore-fixup-amend-commits=<value>` | Not Available |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    ignore-fixup-amend-commits=false
    ```

=== ":octicons-terminal-16:  CLI"
    ```sh
    gitlint -c general.ignore-fixup-amend-commits=false
    ```


## ignore-squash-commits
[:octicons-tag-24: v0.9.0][v0.9.0]

Whether or not to ignore [squash](https://git-scm.com/docs/git-commit#git-commit---squashltcommitgt) commits.

| Default value   | Type            | CLI flag                                   | Env var       |
| --------------- | --------------- | ------------------------------------------ | ------------- |
| `#!python true` | `#!python bool` | `-c general.ignore-squash-commits=<value>` | Not Available |


=== ":octicons-file-code-16:  .gitlint"

    ```ini
    [general]
    ignore-squash-commits=false
    ```

=== ":octicons-terminal-16:  CLI"

    ```sh
    gitlint -c general.ignore-squash-commits=false
    ```