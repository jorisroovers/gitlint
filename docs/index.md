# Introduction
Gitlint is a git commit message linter written in python: it checks your commit messages for style.

Great for use as a [commit-msg git hook](#using-gitlint-as-a-commit-msg-hook) or as part of your gating script in a
[CI pipeline (e.g. Jenkins)](index.md#using-gitlint-in-a-ci-environment).

<script type="text/javascript" src="https://asciinema.org/a/30477.js" id="asciicast-30477" async></script>

!!! note
    **Gitlint support for Windows is experimental**, and [there are some known issues](https://github.com/jorisroovers/gitlint/issues?q=is%3Aissue+is%3Aopen+label%3Awindows).

    Also, gitlint is not the only git commit message linter out there, if you are looking for an alternative written in a different language,
    have a look at [fit-commit](https://github.com/m1foley/fit-commit) (Ruby),
    [node-commit-msg](https://github.com/clns/node-commit-msg) (Node.js) or [commitlint](http://marionebl.github.io/commitlint) (Node.js).

## Features
 - **Commit message hook**: [Auto-trigger validations against new commit message right when you're committing](#using-gitlint-as-a-commit-msg-hook). Also [works with pre-commit](#using-gitlint-through-pre-commit).
 - **Easily integrated**: Gitlint is designed to work [with your own scripts or CI system](#using-gitlint-in-a-ci-environment).
 - **Sane defaults:** Many of gitlint's validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
[community](http://addamhardy.com/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks.html),
[standards](http://chris.beams.io/posts/git-commit/), others are based on checks that we've found
useful throughout the years.
 - **Easily configurable:** Gitlint has sane defaults, but [you can also easily customize it to your own liking](configuration.md).
 - **Community contributed rules**: Conventions that are common but not universal [can be selectively enabled](contrib_rules).
 - **User-defined rules:** Want to do more then what gitlint offers out of the box? Write your own [user defined rules](user_defined_rules.md).
 - **Broad python version support:** Gitlint supports python versions 2.7, 3.5+, PyPy2 and PyPy3.5.
 - **Full unicode support:** Lint your Russian, Chinese or Emoji commit messages with ease!
 - **Production-ready:** Gitlint checks a lot of the boxes you're looking for: actively maintained, high unit test coverage, integration tests,
   python code standards (pep8, pylint), good documentation, widely used, proven track record.

## Getting Started
### Installation
```sh
# Pip is recommended to install the latest version
pip install gitlint

# macOS
brew tap rockyluke/devops
brew install gitlint

# Ubuntu
apt-get install gitlint

# Docker: https://hub.docker.com/r/jorisroovers/gitlint
docker run --ulimit nofile=1024 -v $(pwd):/repo jorisroovers/gitlint
# NOTE: --ulimit is required to work around a limitation in Docker
# Details: https://github.com/jorisroovers/gitlint/issues/129
```

### Usage
```sh
# Check the last commit message
gitlint
# Alternatively, pipe a commit message to gitlint:
cat examples/commit-message-1 | gitlint
# or
git log -1 --pretty=%B | gitlint
# Or read the commit-msg from a file, like so:
gitlint --msg-filename examples/commit-message-2
# Lint all commits in your repo
gitlint --commits HEAD

# To install a gitlint as a commit-msg git hook:
gitlint install-hook
```

Output example:
```sh
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

## Configuration

For in-depth documentation of general and rule-specific configuration options, have a look at the [Configuration](configuration.md) and [Rules](rules.md) pages.

Short example `.gitlint` file ([full reference](configuration.md)):

```ini
[general]
# Ignore certain rules (comma-separated list), you can reference them by
# their id or by their full name
ignore=body-is-missing,T3

# Ignore any data send to gitlint via stdin
ignore-stdin=true

# Configure title-max-length rule, set title length to 80 (72 = default)
[title-max-length]
line-length=80

# You can also reference rules by their id (B1 = body-max-line-length)
[B1]
line-length=123
```

Example use of flags:

```sh
# Change gitlint's verbosity.
$ gitlint -v
# Ignore certain rules
$ gitlint --ignore body-is-missing,T3
# Enable debug mode
$ gitlint --debug
# Load user-defined rules (see http://jorisroovers.github.io/gitlint/user_defined_rules)
$ gitlint --extra-path /home/joe/mygitlint_rules
```

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
                           (e.g.: -c T1.line-length=80). Flag can be used
                           multiple times to set multiple config values.
  --commits TEXT           The range of commits to lint. [default: HEAD]
  -e, --extra-path PATH    Path to a directory or python module with extra
                           user-defined rules
  --ignore TEXT            Ignore rules (comma-separated by id or name).
  --contrib TEXT           Contrib rules to enable (comma-separated by id or
                           name).
  --msg-filename FILENAME  Path to a file containing a commit-msg.
  --ignore-stdin           Ignore any stdin data. Useful for running in CI
                           server.
  --staged                 Read staged commit meta-info from the local
                           repository.
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


## Using gitlint as a commit-msg hook
_Introduced in gitlint v0.4.0_

You can also install gitlint as a git `commit-msg` hook so that gitlint checks your commit messages automatically
after each commit.

```sh
gitlint install-hook
# To remove the hook
gitlint uninstall-hook
```

!!! important

    Gitlint cannot work together with an existing hook. If you already have a `.git/hooks/commit-msg`
    file in your local repository, gitlint will refuse to install the `commit-msg` hook. Gitlint will also only
    uninstall unmodified commit-msg hooks that were installed by gitlint.
    If you're looking to use gitlint in conjunction with other hooks, you should consider
    [using gitlint with pre-commit](#using-gitlint-through-pre-commit).

## Using gitlint through [pre-commit](https://pre-commit.com)

`gitlint` can be configured as a plugin for the `pre-commit` git hooks
framework.  Simply add the configuration to your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # Fill in a tag / sha here
    hooks:
    -   id: gitlint
```

You then need to install the pre-commit hook like so:
```sh
pre-commit install --hook-type commit-msg
```
!!! important

    It's important that you run `pre-commit install --hook-type commit-msg`, even if you've already used
    `pre-commit install` before. `pre-commit install` does **not** install commit-msg hooks by default!

To manually trigger gitlint using `pre-commit` for your last commit message, use the following command:
```sh
pre-commit run gitlint --hook-stage commit-msg --commit-msg-filename .git/COMMIT_EDITMSG
```

In case you want to change gitlint's behavior, you should either use a `.gitlint` file
(see [Configuration](configuration.md)) or modify the gitlint invocation in
your `.pre-commit-config.yaml` file like so:
```yaml
-   repo: https://github.com/jorisroovers/gitlint
    rev:  # Fill in a tag / sha here
    hooks:
    -   id: gitlint
        stages: [commit-msg]
        entry: gitlint
        args: [--contrib=CT1, --msg-filename]
```

## Using gitlint in a CI environment
By default, when just running `gitlint` without additional parameters, gitlint lints the last commit in the current
working directory.

This makes it easy to use gitlint in a CI environment (Jenkins, TravisCI, Github Actions, pre-commit, CircleCI, Gitlab, etc).
In fact, this is exactly what we do ourselves: on every commit,
[we run gitlint as part of our CI checks](https://github.com/jorisroovers/gitlint/blob/v0.12.0/run_tests.sh#L133-L134).
This will cause the build to fail when we submit a bad commit message.

Alternatively, gitlint will also lint any commit message that you feed it via stdin like so:
```sh
# lint the last commit message
git log -1 --pretty=%B | gitlint
# lint a specific commit: 62c0519
git log -1 --pretty=%B 62c0519 | gitlint
```
Note that gitlint requires that you specify `--pretty=%B` (=only print the log message, not the metadata),
future versions of gitlint might fix this and not require the `--pretty` argument.

## Linting a range of commits

_Introduced in gitlint v0.9.0 (experimental in v0.8.0)_

Gitlint allows users to commit a number of commits at once like so:

```sh
# Lint a specific commit range:
gitlint --commits "019cf40...d6bc75a"
# You can also use git's special references:
gitlint --commits "origin..HEAD"
# Or specify a single specific commit in refspec format, like so:
gitlint --commits "019cf40^...019cf40"
```

The `--commits` flag takes a **single** refspec argument or commit range. Basically, any range that is understood
by [git rev-list](https://git-scm.com/docs/git-rev-list) as a single argument will work.

Prior to v0.8.1 gitlint didn't support this feature. However, older versions of gitlint can still lint a range or set
of commits at once by creating a simple bash script that pipes the commit messages one by one into gitlint. This
approach can still be used with newer versions of gitlint in case `--commits` doesn't provide the flexibility you
are looking for.

```sh
#!/bin/sh

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
    lint a large set of commits. Always use `--commits` if you can to avoid this performance penalty.


## Merge, fixup, squash and revert commits
_Introduced in gitlint v0.7.0 (merge), v0.9.0 (fixup, squash) and v0.13.0 (revert)_

**Gitlint ignores merge, revert, fixup and squash commits by default.**

For merge and revert commits, the rationale for ignoring them is
that most users keep git's default messages for these commits (i.e *Merge/Revert "[original commit message]"*).
Often times these commit messages are also auto-generated through tools like github.
These default/auto-generated commit messages tend to cause gitlint violations.
For example, a common case is that *"Merge:"* being auto-prepended triggers a
[title-max-length](rules.md#t1-title-max-length) violation. Most users don't want this, so we disable linting
on Merge and Revert commits by default.

For [squash](https://git-scm.com/docs/git-commit#git-commit---squashltcommitgt) and [fixup](https://git-scm.com/docs/git-commit#git-commit---fixupltcommitgt) commits, the rationale is that these are temporary
commits that will be squashed into a different commit, and hence the commit messages for these commits are very
short-lived and not intended to make it into the final commit history. In addition, by prepending *"fixup!"* or
*"squash!"* to your commit message, certain gitlint rules might be violated
(e.g. [title-max-length](rules.md#t1-title-max-length)) which is often undesirable.

In case you *do* want to lint these commit messages, you can disable this behavior by setting the
general `ignore-merge-commits`, `ignore-revert-commits`,  `ignore-fixup-commits` or
`ignore-squash-commits` option to `false`
[using one of the various ways to configure gitlint](configuration.md).

## Ignoring commits
_Introduced in gitlint v0.10.0_

You can configure gitlint to ignore specific commits or parts of a commit.

One way to do this, is to by [adding a gitline-ignore line to your commit message](configuration.md#commit-specific-config).

If you have a case where you want to ignore a certain type of commits all-together, you can
use gitlint's *ignore* rules.
Here's an example gitlint file that configures gitlint to ignore rules `title-max-length` and `body-min-length`
for all commits with a title starting with *"Release"*.

```ini
[ignore-by-title]
# Match commit titles starting with Release
regex=^Release(.*)
ignore=title-max-length,body-min-length
# ignore all rules by setting ignore to 'all'
# ignore=all

[ignore-by-body]
# Match commits message bodies that have a line that contains 'release'
regex=(.*)release(.*)
ignore=all
```

If you just want to ignore certain lines in a commit, you can do that using the
[ignore-body-lines](rules.md#i3-ignore-body-lines) rule.

```ini
# Ignore all lines that start with 'Co-Authored-By'
[ignore-body-lines]
regex=^Co-Authored-By
```

!!! note

    If you want to implement more complex ignore rules according to your own logic, you can do so using [user-defined
    configuration rules](user_defined_rules.md#configuration-rules).

!!! warning

    When ignoring specific lines, gitlint will no longer be aware of them while applying other rules.
    This can sometimes be confusing for end-users, especially as line numbers of violations will typically no longer
    match line numbers in the original commit message. Make sure to educate your users accordingly.


## Exit codes
Gitlint uses the exit code as a simple way to indicate the number of violations found.
Some exit codes are used to indicate special errors as indicated in the table below.

Because of these special error codes and the fact that
[bash only supports exit codes between 0 and 255](http://tldp.org/LDP/abs/html/exitcodes.html), the maximum number
of violations counted by the exit code is 252. Note that gitlint does not have a limit on the number of violations
it can detect, it will just always return with exit code 252 when the number of violations is greater than or equal
to 252.

Exit Code  | Description
-----------|------------------------------------------------------------
253        | Wrong invocation of the `gitlint` command.
254        | Something went wrong when invoking git.
255        | Invalid gitlint configuration