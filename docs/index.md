# Intro #
Gitlint is a git commit message linter written in python: it checks your commit messages for style.

Great for use as a [commit-msg git hook](#using-gitlint-as-a-commit-msg-hook) or as part of your gating script in a
[CI pipeline (e.g. Jenkins)](index.md#using-gitlint-in-a-ci-environment).

<script type="text/javascript" src="https://asciinema.org/a/30477.js" id="asciicast-30477" async></script>

!!! note
    Gitlint is not the only git commit message linter out there, if you are looking for an alternative written in a different language,
    have a look at [fit-commit](https://github.com/m1foley/fit-commit) (Ruby) or
    [node-commit-msg](https://github.com/clns/node-commit-msg) (Node.js).

## Features ##
 - **Commit message hook**: [Auto-trigger validations against new commit message right when you're committing](#using-gitlint-as-a-commit-msg-hook).
 - **Easily integrated**: Gitlint will validate any git commit message you give it via standard input.
   Perfect for [integration with your own scripts or CI system](#using-gitlint-in-a-ci-environment).
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

```no-highlight
$ gitlint --help
Usage: gitlint [OPTIONS] COMMAND [ARGS]...

  Git lint tool, checks your git commit messages for styling issues

Options:
  --target DIRECTORY       Path of the target git repository. [default:
                           current working directory]
  -C, --config PATH        Config file location [default: .gitlint]
  -c TEXT                  Config flags in format <rule>.<option>=<value>
                           (e.g.: -c T1.line-length=80). Flag can be used
                           multiple times to set multiple config values.
  --commits TEXT           The range of commits to lint. [default: HEAD]
  -e, --extra-path PATH    Path to a directory or python module with extra
                           user-defined rules
  --ignore TEXT            Ignore rules (comma-separated by id or name).
  --msg-filename FILENAME  Path to a file containing a commit-msg
  -v, --verbose            Verbosity, more v's for more verbose output (e.g.:
                           -v, -vv, -vvv). [default: -vvv]
  -s, --silent             Silent mode (no output). Takes precedence over -v,
                           -vv, -vvv.
  -d, --debug              Enable debugging output.
  --version                Show the version and exit.
  --help                   Show this message and exit.

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

## Using gitlint through [pre-commit](https://pre-commit.com)

`gitlint` can be configured as a plugin for the `pre-commit` git hooks
framework.  Simply add the configuration to your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # Fill in a tag / sha here
    hooks:
    -   id: gitlint
```


## Using gitlint in a CI environment ##
By default, when just running ```gitlint``` without additional parameters, gitlint lint the last commit in the current
git repository.

This makes it easy to add gitlint to a check script that is run in a CI environment (Jenkins, TravisCI, pre-commit,
CircleCI, etc).
In fact, this is exactly what we do ourselves: on every commit,
[we run gitlint as part of our travisCI tests](https://github.com/jorisroovers/gitlint/blob/v0.7.1/run_tests.sh#L62-L65).
This will cause the build to fail when we submit a bad commit message.


!!! note
    Versions prior to gitlint 0.9.0 required a TTY to be attached to STDIN for this to work, this is no longer required
    now.

Alternatively, gitlint will also lint any commit message that you feed it via stdin like so:
```bash
# lint the last commit message
git log -1 --pretty=%B | gitlint
# lint a specific commit: 62c0519
git log -1 --pretty=%B 62c0519 | gitlint
```
Note that gitlint requires that you specify ```--pretty=%B``` (=only print the log message, not the metadata),
future versions of gitlint might fix this and not require the ```--pretty``` argument.

## Linting a range of commits ##
_Experimental support introduced in gitlint v0.8.1, known issues:_
_[#23](https://github.com/jorisroovers/gitlint/pull/23)_

Gitlint allows users to commit a number of commits at once like so:

```bash
# Lint a specific commit range:
gitlint --commits 019cf40...d6bc75a
# You can also use git's special references:
gitlint --commits origin..HEAD
# Or specify a single specific commit:
gitlint --commits 6f29bf81a8322a04071bb794666e48c443a90360
```

The ```--commits``` flag takes a **single** refspec argument or commit range. Basically, any range that is understood
by [git rev-list](https://git-scm.com/docs/git-rev-list) as a single argument will work.

Prior to v0.8.1 gitlint didn't support this feature. However, older versions of gitlint can still lint a range or set
of commits at once by creating a simple bash script that pipes the commit messages one by one into gitlint. This
approach can still be used with newer versions of gitlint in case ```--commits``` doesn't provide the flexibility you
are looking for.

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
    lint a large set of commits. Always use ```--commits``` if you can to avoid this performance penalty.


## Merge, fixup and squash commits ##
_Introduced in gitlint v0.7.0 (merge commits) and gilint v0.9.0 (fixup, squash)_

**Gitlint ignores merge, fixup and squash commits by default.**

For merge commits, the rationale for ignoring them is
that in many cases merge commits are not created by users themselves but by tools such as github,
[gerrit](https://code.google.com/p/gerrit/) and others. These tools often generate merge commit messages that
violate gitlint's set of rules (a common example is *"Merge:"* being auto-prepended  which can trigger a
[title-max-length](rules.md#t1-title-max-length) violation)
and it's not always convenient or desired to change those.

For [squash](https://git-scm.com/docs/git-commit#git-commit---squashltcommitgt) and [fixup](https://git-scm.com/docs/git-commit#git-commit---fixupltcommitgt) commits, the rationale is that these are temporary
commits that will be squashed into a different commit, and hence the commit messages for these commits are very
short-lived and not intended to make it into the final commit history. In addition, by prepending *"fixup!"* or
*"squash!"* to your commit message, certain gitlint rules might be violated
(e.g. [title-max-length](rules.md#t1-title-max-length)) which is often undesirable.

In case you *do* want to lint these commit messages, you can disable this behavior by setting the
general ```ignore-merge-commits```, ```ignore-fixup-commits``` or ```ignore-squash-commits``` option to ```false```
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

