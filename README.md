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
# Alternatively, pipe a commit message to gitlint
cat examples/commit-message-1 | gitlint
```

NOTE: The returned exit code equals the number of errors found.

Other commands and variations:

```bash
Usage: gitlint [OPTIONS] PATH

Git lint tool, checks your git commit messsages for styling issues

Options:
  --config PATH  Config file location (default: .gitlint).
  --ignore TEXT  Ignore rules (comma-separated by id or name).
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
```

## Supported Rules ##

ID    | Name                | Description
------|---------------------|----------------------------------------------------
R1    | max-line-length     | Line length must be &lt; 80 chars.
R2    | trailing-whitespace | Line cannot have trailing whitespace (space or tab)
R3    | hard-tabs           | Line contains hard tab characters (\t)


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
