# gitlint #

[![Build Status](https://travis-ci.org/jorisroovers/gitlint.svg?branch=master)]
(https://travis-ci.org/jorisroovers/gitlint)
[![PyPi Package](https://img.shields.io/pypi/v/gitlint.png)]
(https://pypi.python.org/pypi/gitlint)

Git commit message linter written in python, checks your commit messages for style.

Great for use as a ```commit-msg``` git hook or as part of your gating script in a CI/CD pipeline (e.g. jenkins).

Many of the gitlint validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
[community](http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/)
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
# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint
# or
git log -1 --pretty=%B | gitlint

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
NOTE: The returned exit code equals the number of errors found. The exit code ```10000``` is used when gitlint hits a
configuration error.

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


## Rules ##

ID    | Name                        | Description
------|-----------------------------|----------------------------------------------------
T1    | title-max-length            | Title length must be &lt; 72 chars.
T2    | title-trailing-whitespace   | Title cannot have trailing whitespace (space or tab)
T3    | title-trailing-punctuation  | Title cannot have trailing punctuation (?:!.,;)
T4    | title-hard-tab              | Title cannot contain hard tab characters (\t)
T5    | title-must-not-contain-word | Title cannot contain certain words (default: "WIP")
T6    | title-leading-whitespace    | Title cannot have leading whitespace (space or tab)
B1    | body-max-line-length        | Lines in the body must be &lt; 80 chars
B2    | body-trailing-whitespace    | Body cannot have trailing whitespace (space or tab)
B3    | body-hard-tab               | Body cannot contain hard tab characters (\t)
B4    | body-first-line-empty       | First line of the body (second line of commit message) must be empty
B5    | body-min-length             | Body length must be at least 20 characters
B6    | body-is-missing             | Body message must be specified
B7    | body-changed-file-mention   | Body must contain references to certain files if those files are changed in the last commit

## Configuration ##

You can modify gitlint's behavior by specifying a config file like so: 
```bash
gitlint --config myconfigfile 
```
By default, gitlint will look for an optional ```.gitlint``` file for configuration.

```ini
[general]
ignore=title-trailing-punctuation, T3
# verbosity should be a value between 1 and 3, the commandline -v flags take precedence over
# this
verbosity = 2

[title-max-length]
line-length=20

[B1]
# B1 = body-max-line-length
line-length=30

[title-must-not-contain-word]
# Comma-seperated list of words that should not occur in the title. Matching is case
# insensitive. It's fine if the keyword occurs as part of a larger word (so "WIPING"
# will not cause a violation, but "WIP: my title" will.
words=wip,title

[body-min-length]
min-length=5

[body-changed-file-mention]
# List of files that need to be explicitly mentioned in the body when they are changed
# This is useful for when developers often erroneously edit certain files or git submodules.
# By specifying this rule, developers can only change the file when they explicitly reference
# it in the commit message.
files=gitlint/rules.py,README.md
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


## Using gitlint as a commit-msg hook ##
You can also install gitlint as a git ```commit-msg``` hook so that gitlint checks your commit messages automatically
after each commit.

```bash
gitlint --install-hook
```

Important Notes:

- You currently cannot uninstall the ```commit-msg``` hook using gitlint. You will need to manually remove the hook from
  ```.git/hooks/commit-msg``` in your local git repository.
- Gitlint cannot work together with an existing hook. If you already have a ```.git/hooks/commit-msg``` file in your
  local repository, gitlint will refuse to install the ```commit-msg``` hook.


## Contributing ##

We'd love for you to contribute to gitlint. Just open a pull request and we'll get right on it! 
You can find a wishlist below, but we're open to any suggestions you might have!

### Development ###

There is a Vagrantfile in this repository that can be used for development.
```bash
vagrant up
vagrant ssh
```

Or you can choose to use your local environment:

```bash
virtualenv .venv
pip install -r requirements.txt -r test-requirements.txt
python setup.py develop
```

To run tests:
```bash
./run_tests.sh                       # run unit tests and print test coverage
./run_tests.sh --no-coverage         # run unit tests without test coverage
./run_tests.sh --pep8                # pep8 checks
./run_tests.sh --stats               # print some code stats
```

To see the package description in HTML format
```
pip install docutils
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python setup.py --long-description | rst2html.py > output.html
```

## Wishlist ##
- More rules: 
    - title-regex: Title must match a given regex
    - Checkbox rules: Developers must add a line to the end of the commit specifying that they've considered
      a number of aspects when committing the code. E.g.: ```gitlint-checks: tests, documentation```.
      This can be useful as a reminder if developers often submit code without updating the documentation or tests.
    - Overwrite rules: In some cases, gitlint config might need to disabled/overwritten for a specific commit. This
      could be done using by adding lines similar to ```gitlint: disable``` or
      ```gitlint-config: general.ignore=T2, T1.line-length=100``` to the commit message.
    - ...
- More rule options:
    - title-must-not-contain-word: case sensitive match
    - title-trailing-punctuation: define punctuation
- Git hooks:
    - uninstall of gitlint ```commit-msg``` hook (only uninstall if the hook is a gitlint hook)
    - appending to an existing hook (after user confirmation)
- Check a range of commit messages at once (similar to how git log works, eg.: ```git log -3```)
- Rules for different attributes of the the commit message: author, date, etc
- Developer convenience:
    - run_tests.sh: Run specific tests
    - More unit tests, always more unit tests
