# Configuration
Gitlint provides multiple ways to configure its behavior:

1. **[`.gitlint` file](gitlint_file.md)** (Recommended)
2. **[CLI flags and environment variables](cli.md)**
3. **[Config in your commit message](commit_config.md)**

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

    ### Configuring rules ##########################################################

    [title-max-length] # reference rules by name or id
    line-length=80     # rule option 

    [title-min-length]
    min-length=5
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
    ```


## Configuration

For in-depth documentation of general and rule-specific configuration options, have a look at the [Configuration](configuration.md) and [Rules](rules.md) pages.

Short example `.gitlint` file ([full reference](configuration.md)):

```ini
[general]
# Ignore certain rules (comma-separated list), you can reference them by
# their id or by their full name
ignore=body-is-missing,T3

# Ignore any data sent to gitlint via stdin
ignore-stdin=true

# Configure title-max-length rule, set title length to 80 (72 = default)
[title-max-length]
line-length=80

# You can also reference rules by their id (B1 = body-max-line-length)
[B1]
line-length=123
```

Example use of flags:

```sh
# Change gitlint's verbosity.
$ gitlint -v
# Ignore certain rules
$ gitlint --ignore body-is-missing,T3
# Enable debug mode
$ gitlint --debug
# Load user-defined rules (see http://jorisroovers.github.io/gitlint/user_defined_rules)
$ gitlint --extra-path /home/joe/mygitlint_rules
```




## Configuration precedence
gitlint configuration is applied in the following order of precedence:

1. Commit specific config (e.g.: `gitlint-ignore: all` in the commit message)
2. Configuration Rules (e.g.: [ignore-by-title](rules.md#i1-ignore-by-title))
3. Commandline convenience flags (e.g.:  `-vv`, `--silent`, `--ignore`)
4. Environment variables (e.g.: `GITLINT_VERBOSITY=3`)
5. Commandline configuration flags (e.g.: `-c title-max-length=123`)
6. Configuration file (local `.gitlint` file, or file specified using `-C`/`--config`)
7. Default gitlint config
