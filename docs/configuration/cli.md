# Commandline config

You can also use one or more `-c` flags like so:

```
$ gitlint -c general.verbosity=2 -c title-max-length.line-length=80 -c B1.line-length=100
```
The generic config flag format is `-c <rule>.<option>=<value>` and supports all the same rules and options which
you can also use in a `.gitlint` config file.

Other commands and variations:

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