# gitlint #

[![Build Status](https://travis-ci.org/jorisroovers/gitlint.svg?branch=master)]
(https://travis-ci.org/jorisroovers/gitlint)
[![PyPi Package](https://img.shields.io/pypi/v/gitlint.png)]
(https://pypi.python.org/pypi/gitlint)

Git commit message linter written in python.

Great for use in a test script in your CI/CD pipeline (e.g. jenkins). Git hook support coming soon!

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
# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint
# or
git log -1 --pretty=%B | gitlint
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
NOTE: The returned exit code equals the number of errors found.

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

```bash
Usage: gitlint [OPTIONS]

  Git lint tool, checks your git commit messages for styling issues

Options:
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


## Configuration ##

You can modify gitlint's behavior by specifying a config file like so: 
```bash
gitlint --config myconfigfile 
```
By default, gitlint will look for an optional ```.gitlint``` file for configuration.

```
[general] 
ignore=title-trailing-punctuation, T3
# verbosity should be a value between 1 and 3, the commandline -v flags take precedence over this
verbosity = 2

[title-max-length]
line-length=20

[B1]
# B1 = body-max-line-length
line-length=30

[title-must-not-contain-word]
# Comma-seperated list of words that should not occur in the title. Matching is case insensitive.
# It's fine if the keyword occurs as part of a larger word (so "WIPING" will not cause a violation,
# but "WIP: my title" will.
words=wip,title
```

Alternatively, you can use one or more ```-c``` flags like so:

```
$ gitlint -c general.verbosity=2 -c title-max-length.line-length=80 -c B1.line-length=100
```
The generic config flag format is ```-c <rule>.<option>=<value>``` and supports all the same rules and options which 
you can also use in a ```.gitlint``` config file.

### Config precedence ###
gitlint's behavior can be configured in a couple of different ways.  Different config options take the following order
of precedence:
1. Commandline convenience flags (e.g.:  ```-vv```, ```--silent```, ```--ignore```)
2. Commandline configuration flags (e.g.: ```-c title-max-length=123```)
3. Configuration file (local ```.gitlint``` file, or file specified using ```-C```/```--config```)
4. Default gitlint config

## Supported Rules ##

ID    | Name                        | Description
------|-----------------------------|----------------------------------------------------
T1    | title-max-length            | Title length must be &lt; 72 chars.
T2    | title-trailing-whitespace   | Title cannot have trailing whitespace (space or tab)
T3    | title-trailing-punctuation  | Title cannot have trailing punctuation (?:!.,;)
T4    | title-hard-tab              | Title cannot contain hard tab characters (\t)
T5    | title-must-not-contain-word | Title cannot contain certain words (default: "WIP"). Matching is case insensitive. It's fine if the keyword occurs as part of a larger word (so "WIPING" will not cause a violation, but "WIP: my title" will.
B1    | body-max-line-length        | Lines in the body must be &lt; 80 chars.            
B2    | body-trailing-whitespace    | Body cannot have trailing whitespace (space or tab)
B3    | body-hard-tab               | Body cannot contain hard tab characters (\t)
B4    | body-first-line-empty       | First line of the body (second line of commit message) must be empty

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
- More rules: 
    - title-regex: Title must match a given regex
    - changed-file-mentioned: If a specific file is changed, it needs to be explicitly mentioned in the commit message
    - ...
- More rule options:
    - title-must-not-contain-word: case sensitive match
    - title-trailing-punctuation: define punctuation

- More unit tests :D
- Check a range of commit messages at once (similar to how git log works, eg.: ```git log -3```)
- Rules for different attributes of the the commit message: author, date, etc
- Git commit hooks
