# gitlint

[![Build Status](https://travis-ci.org/jorisroovers/gitlint.svg?branch=master)]
(https://travis-ci.org/jorisroovers/gitlint)
[![PyPi Package](https://img.shields.io/pypi/v/gitlint.png)]
(https://pypi.python.org/pypi/gitlint)

Git linter written in python.

**NOTE: gitlint is still under active development and missing many core features**

NOTE: The returned exit code equals the number of errors found.

Other commands and variations:

```bash
Usage: gitlint [OPTIONS] PATH

Git lint tool, checks your git commit messsages for styling issues

Options:
  --config PATH  Config file location (default: .markdownlint).
  --ignore TEXT  Ignore rules (comma-separated by id or name).
  --version      Show the version and exit.
  --help         Show this message and exit.
```

You can modify pymarkdownlint's behavior by specifying a config file like so: 
```bash
markdownlint --config myconfigfile 
```
By default, markdownlint will look for an **optional** ```.markdownlint``` file for configuration.

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
