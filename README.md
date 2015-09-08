# gitlint

[![Build Status](https://travis-ci.org/jorisroovers/gitlint.svg?branch=master)]
(https://travis-ci.org/jorisroovers/gitlint)
[![PyPi Package](https://img.shields.io/pypi/v/gitlint.png)]
(https://pypi.python.org/pypi/gitlint)

Git linter written in python. Checks your git log for style.

**NOTE: gitlint is still under active development**

Get started by running:
```bash
# Check the last commit message
gitlint
# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint
# Lint the third latest git commit message
cat git log -3 -1 | gitlint
```

NOTE: The returned exit code equals the number of errors found.

Other commands and variations:

```bash
Usage: gitlint [OPTIONS]

  Git lint tool, checks your git commit messages for styling issues

Options:
  --config PATH  Config file location (default: .gitlint).
  --ignore TEXT  Ignore rules (comma-separated by id or name).
  -v, --verbose  Verbosity, more v's for more verbose output (e.g.: -v, -vv,
                 -vvv). Default: -vvv
  -s, --silent   Silent mode (no output).
  --version      Show the version and exit.
  --help         Show this message and exit.
```

You can modify gitlint's behavior by specifying a config file like so: 
```bash
gitlint --config myconfigfile 
```
By default, gitlint will look for an **optional** ```.gitlint``` file for configuration.

## Config file ##

```
[general]
# rules can be ignored by name or by id
ignore=max-line-length, R3
# verbosity level: 0-3 (default: 2)
verbosity=3
```

## Supported Rules ##

ID    | Name                | Description
------|-----------------------------|----------------------------------------------------
T1    | title-max-length            | Title length must be &lt; 80 chars.
T2    | title-trailing-whitespace   | Title cannot have trailing whitespace (space or tab)
T3    | title-trailing-punctuation  | Title cannot have trailing punctuation (?:!.,;)
T4    | title-hard-tab              | Title cannot contain hard tab characters (\t)
T5    | title-must-not-contain-word | Title cannot contain certain words (default: "WIP")
B1    | body-max-line-length        | Lines in the body must be &lt; 80 chars.            
B2    | body-trailing-whitespace    | Body cannot have trailing whitespace (space or tab)
B3    | body-hard-tab               | Body cannot contain hard tab characters (\t)

## Development ##

To run tests:
```bash
./run_tests.sh                       # run unit tests and print test coverage
./run_tests.sh --no-coverage         # run unit tests without test coverage
./run_tests.sh --pep8                # pep8 checks
./run_tests.sh --stats               # print some code stats
```

There is a Vagrantfile in this repository that can be used for development.
```bash
vagrant up
vagrant ssh
```

## Wishlist ##
- Check the entire git log
- Check a specific commit or range of commits, similar to how git log works, eg.:
  git log -1 -3
- More rules:
   - title-contains, title-not-contains    
- Checks on different attributes of the the commit message: author, date, etc
