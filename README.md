# gitlint #

[![Build Status](https://travis-ci.org/jorisroovers/gitlint.svg?branch=master)]
(https://travis-ci.org/jorisroovers/gitlint)
[![Coverage Status](https://coveralls.io/repos/jorisroovers/gitlint/badge.svg?branch=master&service=github)]
(https://coveralls.io/github/jorisroovers/gitlint?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/gitlint.png)]
(https://pypi.python.org/pypi/gitlint)

Git commit message linter written in python, checks your commit messages for style.

Great for use as a ```commit-msg``` git hook or as part of your gating script in a CI/CD pipeline (e.g. jenkins).

See [jorisroovers.github.io/gitlint/](http://jorisroovers.github.io/gitlint/) for full documentation.

Many of the gitlint validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
[community](http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/),
[standards](http://chris.beams.io/posts/git-commit/), others are based on checks that we've found
useful throughout the years. Gitlint has sane defaults, but you can also easily customize it to your own liking.

Note that not all features described below might be available in the latest stable version. Have a look at the
[Changelog](CHANGELOG.md) for details.

If you are looking for an alternative written in Ruby, have a look at
[fit-commit](https://github.com/m1foley/fit-commit).

## Getting Started ##
```bash
# Install gitlint
pip install gitlint

# Check the last commit message
gitlint
# Output
# 1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
# 1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
# 1: T4 Title contains hard tab characters (\t): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
# 2: B4 Second line is not empty: "This line should not contain text"
# [truncated]

# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint

# To install a gitlint as a commit-msg git hook:
gitlint --install-hook
```

Output example:
```bash
$ cat examples/commit-message-2 | gitlint
1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T4 Title contains hard tab characters (\t): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
2: B4 Second line is not empty: "This line should not contain text"
3: B1 Line exceeds max length (125>80): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B2 Line has trailing whitespace: "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
3: B3 Line contains hard tab characters (\t): "Lines typically need to have 	a max length, meaning that they can't exceed a preset number of characters, usually 80 or 120. "
```
NOTE: The returned exit code equals the number of errors found. [Some exit codes are special](README.md#exit-codes).

You can modify verbosity using the ```-v``` flag, like so:
```bash
$ cat examples/commit-message-2 | gitlint -v
1: T1
1: T2
[removed output]
$ cat examples/commit-message-2 | gitlint -vv
1: T1 Title exceeds max length (134>80)
1: T2 Title has trailing whitespace
1: T4 Title contains hard tab characters (\t)
[removed output]
$ cat examples/commit-message-2 | gitlint -vvv
1: T1 Title exceeds max length (134>80): "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
1: T2 Title has trailing whitespace: "This is the title of a commit message that 	is over 80 characters and contains hard tabs and trailing whitespace and the word wiping  "
[removed output]
```
The default verbosity is ```-vvv```.

Other commands and variations:

```
Usage: gitlint [OPTIONS]

  Git lint tool, checks your git commit messages for styling issues

Options:
  --install-hook     Install gitlint as a git commit-msg hook
  --uninstall-hook   Uninstall gitlint commit-msg hook
  -C, --config PATH  Config file location (default: .gitlint).
  -c TEXT            Config flags in format <rule>.<option>=<value> (e.g.: -c
                     T1.line-length=80). Flag can be used multiple times to
                     set multiple config values.
  --ignore TEXT      Ignore rules (comma-separated by id or name).
  -v, --verbose      Verbosity, more v's for more verbose output (e.g.: -v,
                     -vv, -vvv). Default: -vvv
  -s, --silent       Silent mode (no output). Takes precedence over -v, -vv,
                     -vvv.
  --version          Show the version and exit.
  --help             Show this message and exit.
```


## Contributing ##
All contributions are welcome!
See [jorisroovers.github.io/gitlint/contributing](http://jorisroovers.github.io/gitlint/contributing) for details on
how to get started - it's easy!

## Wishlist ##
- More rules: 
    - Checkbox rules: Developers must add a line to the end of the commit specifying that they've considered
      a number of aspects when committing the code. E.g.: ```gitlint-checks: tests, documentation```.
      This can be useful as a reminder if developers often submit code without updating the documentation or tests.
    - max-lines-change: Maximum lines of change in a single commit (-1 = unlimited)
    - Rules for different attributes of the the commit message: author, date, etc
- More rule options:
    - title-must-not-contain-word: case sensitive match
    - title-trailing-punctuation: define punctuation
- Rule improvements:
    - body-changed-file-mention: list all files/directories that need to be mentioned as part of the violation
    - body-changed-file-mention: distinction between change file and directory in output
- Git hooks:
    - appending to an existing hook (after user confirmation)
- Reporting:
    - ```--summary``` option: print out a summary at the end. Contains: number/type or errors
    - ```--count``` option: only print out the number of violations
    - ```--report```: html report
- Configuration
    - Work on a different git repo than the current directory: ```--target``` parameter.
- Documentation 
    - Create demo using [https://asciinema.org/]()
- Developer convenience:
    - More unit tests, always more unit tests
    - Integration tests
