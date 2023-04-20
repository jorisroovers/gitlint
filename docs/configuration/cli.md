# Commandline config

Gitlint behavior can be changed by various commandline flags and environment variables.

There's 2 categories of these:

1. [**General options**](general_options.md): configure gitlint's overall behavior
2. **Rule specific options**: configure how specific rules behave

To set `general` options ([full reference](general_options.md)) via the CLI, there's a number of convenience flags and environment
variables available:

=== ":octicons-terminal-16:  CLI"

    ```sh
    # Mute all output
    gitlint --silent

    # Lint a specific commit
    gitlint --commit abc123
    ```

=== ":material-application-variable-outline: Env var"  

    ```sh
    # Mute all output
    GITLINT_SILENT=1 gitlint

    # Lint a specific commit
    GITLINT_COMMIT=abc123 gitlint
    ```

Alternatively, you can also use one or more `-c` flags like so:

```sh
gitlint -c general.silent=true -c title-max-length.line-length=80
```

The benefit of the `-c` flag is that it can set both `general` options as well as `rule` options.

The generic config flag format is `-c <rule>.<option>=<value>` and supports all the same rules and options which
you can also use in a [`.gitlint` config file](gitlint_file.md).

# All commands and options

```no-highlight
$ gitlint --help
Usage: gitlint [OPTIONS] COMMAND [ARGS]...

  Git lint tool, checks your git commit messages for styling issues

  Documentation: http://jorisroovers.github.io/gitlint

Options:
  --target DIRECTORY       Path of the target git repository. [default:
                           current working directory]
  -C, --config FILE        Config file location [default: .gitlint]
  -c TEXT                  Config flags in format <rule>.<option>=<value>
                           (e.g.: -c T1.line-length=80). Flag can be
                           used multiple times to set multiple config values.
  --commit TEXT            Hash (SHA) of specific commit to lint.
  --commits TEXT           The range of commits (refspec or comma-separated
                           hashes) to lint. [default: HEAD]
  -e, --extra-path PATH    Path to a directory or python module with extra
                           user-defined rules
  --ignore TEXT            Ignore rules (comma-separated by id or name).
  --contrib TEXT           Contrib rules to enable (comma-separated by id or
                           name).
  --msg-filename FILENAME  Path to a file containing a commit-msg.
  --ignore-stdin           Ignore any stdin data. Useful for running in CI
                           server.
  --staged                 Attempt smart guesses about meta info (like
                           author name, email, branch, changed files, etc)
                           for staged commits.
  --fail-without-commits   Hard fail when the target commit range is empty.
  -v, --verbose            Verbosity, more v's for more verbose output
                           (e.g.: -v, -vv, -vvv). [default: -vvv]
  -s, --silent             Silent mode (no output).
                           Takes precedence over -v, -vv, -vvv.
  -d, --debug              Enable debugging output.
  --version                Show the version and exit.
  --help                   Show this message and exit.

Commands:
  generate-config  Generates a sample gitlint config file.
  install-hook     Install gitlint as a git commit-msg hook.
  lint             Lints a git repository [default command]
  run-hook         Runs the gitlint commit-msg hook.
  uninstall-hook   Uninstall gitlint commit-msg hook.

  When no COMMAND is specified, gitlint defaults to 'gitlint lint'.
```