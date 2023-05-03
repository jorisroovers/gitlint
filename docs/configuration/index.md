# Configuration
Gitlint provides multiple ways to configure its behavior:

1. **[`.gitlint` file](gitlint_file.md)** (Recommended)
2. **[CLI flags and environment variables](cli.md)**
3. **[Config in your commit message](commit_config.md)**
4. **[Configuration Rules](../rules/user_defined_rules/configuration_rules.md)**

## Quick start

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

## Configuration precedence
Gitlint configuration is applied in the following order of precedence:

1. Commit specific config (e.g.: `gitlint-ignore: all` in the commit message)
2. Configuration Rules (e.g.: [ignore-by-title](rules.md#i1-ignore-by-title))
3. Commandline convenience flags (e.g.:  `-vv`, `--silent`, `--ignore`)
4. Environment variables (e.g.: `GITLINT_VERBOSITY=3`)
5. Commandline configuration flags (e.g.: `-c title-max-length=123`)
6. Configuration file (local `.gitlint` file, or file specified using `-C`/`--config`)
7. Default gitlint config
