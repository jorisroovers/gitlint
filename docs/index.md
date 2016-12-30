# Intro #
Gitlint is a git commit message linter written in python: it checks your commit messages for style.

Great for use as a ```commit-msg``` git hook or as part of your gating script in a CI/CD pipeline (e.g. jenkins).

<script type="text/javascript" src="https://asciinema.org/a/30477.js" id="asciicast-30477" async></script>

!!! note
    Gitlint is not the only git commit message linter out there, if you are looking for an alternative written in a different language,
    have a look at [fit-commit](https://github.com/m1foley/fit-commit) (Ruby) or
    [node-commit-msg](https://github.com/clns/node-commit-msg) (Node.js).

## Features ##
 - **Commit message hook**: [Auto-trigger validations against new commit message right when you're committing](#using-gitlint-as-a-commit-msg-hook).
 - **Easily integrated**: Gitlint will validate any git commit message you give it via standard input.
   Perfect for [integration with your own scripts or CI system](#using-gitlint-in-a-cicd-script).
 - **Sane defaults:** Many of gitlint's validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
[community](http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/),
[standards](http://chris.beams.io/posts/git-commit/), others are based on checks that we've found
useful throughout the years.
 - **Easily configurable:** Gitlint has sane defaults, but [you can also easily customize it to your own liking](configuration.md).
 - **User-defined Rules:** Want to do more then what gitlint offers out of the box? Write your own [user defined rules](user_defined_rules.md).
 - **Broad python version support:** Gitlint supports python versions 2.6, 2.7, 3.3+ and PyPy2.
 - **Full unicode support:** Lint your Russian, Chinese or Emoji commit messages with ease!
 - **Production-ready:** Gitlint checks a lot of the boxes you're looking for: high unit test coverage, integration tests,
   python code standards (pep8, pylint), good documentation, proven track record.

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
gitlint install-hook
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
!!! note
    The returned exit code equals the number of errors found. [Some exit codes are special](index.md#exit-codes).

For a list of available rules and their configuration options, have a look at the [Rules](rules.md) page.

The [Configuration](configuration.md) page explains how you can modify gitlint's runtime behavior via command-line
flags, a ```.gitlint``` configuration file or on a per commit basis.

As a simple example, you can modify gitlint's verbosity using the ```-v``` flag, like so:
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
$ gitlint --help
Usage: gitlint [OPTIONS] COMMAND [ARGS]...

  Git lint tool, checks your git commit messages for styling issues

Options:
  --target DIRECTORY          Path of the target git repository. [default:
                              current working directory]
  -C, --config PATH           Config file location [default: .gitlint]
  -c TEXT                     Config flags in format <rule>.<option>=<value>
                              (e.g.: -c T1.line-length=80). Flag can be used
                              multiple times to set multiple config values.
  -e, --extra-path DIRECTORY  Path to a directory with extra user-defined
                              rules
  --ignore TEXT               Ignore rules (comma-separated by id or name).
  -v, --verbose               Verbosity, more v's for more verbose output
                              (e.g.: -v, -vv, -vvv). [default: -vvv]
  -s, --silent                Silent mode (no output). Takes precedence over
                              -v, -vv, -vvv.
  -d, --debug                 Enable debugging output.
  --version                   Show the version and exit.
  --help                      Show this message and exit.

Commands:
  generate-config  Generates a sample gitlint config file.
  install-hook     Install gitlint as a git commit-msg hook.
  lint             Lints a git repository [default command]
  uninstall-hook   Uninstall gitlint commit-msg hook.

  When no COMMAND is specified, gitlint defaults to 'gitlint lint'.
```


## Using gitlint as a commit-msg hook ##
_Introduced in gitlint v0.4.0_

You can also install gitlint as a git ```commit-msg``` hook so that gitlint checks your commit messages automatically
after each commit.

```bash
gitlint install-hook
# To remove the hook
gitlint uninstall-hook
```

!!! important

    Gitlint cannot work together with an existing hook. If you already have a ```.git/hooks/commit-msg```
    file in your local repository, gitlint will refuse to install the ```commit-msg``` hook. Gitlint will also only
    uninstall unmodified commit-msg hooks that were installed by gitlint.

## Using gitlint in a CI/CD script ##
By default, when just running ```gitlint``` without additional parameters, gitlint lint the last commit in the current
git repository.

This makes it easy to add gitlint to a check script that is run in a CI environment. In fact, this is exactly what we
do ourselves: on every commit,
[we run gitlint as part of our travisCI tests](https://github.com/jorisroovers/gitlint/blob/v0.7.1/run_tests.sh#L62-L65).
This will cause the build to fail when we submit a bad commit message.

Gitlint will also lint any commit message that you feed it via stdin like so:
```bash
# lint the last commit message
git log -1 --pretty=%B | gitlint
# lint a specific commit: 62c0519
git log -1 --pretty=%B 62c0519 | gitlint
```
For now, it's required that you specify ```--pretty=%B``` (=only print the log message, not the metadata),
future versions of gitlint might fix this.

### Linting a range of commits ###

While gitlint does not yet support linting a range or set of commits at once, it's actually quite easy to do this using
a simple bash script that pipes the commit messages one by one into gitlint.

```bash
#!/bin/bash

for commit in $(git rev-list master); do
    commit_msg=$(git log -1 --pretty=%B $commit)
    echo "$commit"
    echo "$commit_msg" | gitlint
    echo "--------"
done
```
!!! note
    One downside to this approach is that you invoke gitlint once per commit vs. once per set of commits.
    This means you'll incur the gitlint startup time once per commit, making this approach rather slow if you want to
    lint a large set of commits. For reference, at the time of writing, linting gitlint's entire commit log
    (~160 commits) this way took about 12 seconds on a 2015 Macbook Pro.


## Merge commits ##
_Introduced in gitlint v0.7.0_

Gitlint ignores merge commits by default. The rationale behind this is that in many cases
merge commits are not created by users themselves but by tools such as github,
[gerrit](https://code.google.com/p/gerrit/) and others. These tools often generate merge commit messages that
violate gitlint's set of rules and it's not always convenient or desired to change those.

In case you *do* want to lint merge commit messages, you can disable this behavior by setting the
general ```ignore-merge-commits``` option to ```false```
[using one of the various ways to configure gitlint](configuration.md).


## Exit codes ##
Gitlint uses the exit code as a simple way to indicate the number of violations found.
Some exit codes are used to indicate special errors as indicated in the table below.

Because of these special error codes and the fact that
[bash only supports exit codes between 0 and 255](http://tldp.org/LDP/abs/html/exitcodes.html), the maximum number
of violations counted by the exit code is 252. Note that gitlint does not have a limit on the number of violations
it can detect, it will just always return with exit code 252 when the number of violations is greater than or equal
to 252.

Exit Code  | Description
-----------|------------------------------------------------------------
253        | Wrong invocation of the ```gitlint``` command.
254        | Something went wrong when invoking git.
255        | Invalid gitlint configuration

