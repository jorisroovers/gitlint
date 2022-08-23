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


!!! important
    **Gitlint no longer supports Python 2.7 and Python 3.5 as they [have reached End-Of-Life](https://endoflife.date/python). The last gitlint version to support Python 2.7 and Python 3.5 is `0.14.0` (released on October 24th, 2020).**

## Features
 - **Commit message hook**: [Auto-trigger validations against new commit message right when you're committing](#using-gitlint-as-a-commit-msg-hook). Also [works with pre-commit](#using-gitlint-through-pre-commit).
 - **Easily integrated**: Gitlint is designed to work [with your own scripts or CI system](#using-gitlint-in-a-ci-environment).
 - **Sane defaults:** Many of gitlint's validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
[community](https://addamhardy.com/2013-06-05-good-commit-messages-and-enforcing-them-with-git-hooks),
[standards](http://chris.beams.io/posts/git-commit/), others are based on checks that we've found
useful throughout the years.
 - **Easily configurable:** Gitlint has sane defaults, but [you can also easily customize it to your own liking](configuration.md).
 - **Community contributed rules**: Conventions that are common but not universal [can be selectively enabled](contrib_rules).
 - **User-defined rules:** Want to do more then what gitlint offers out of the box? Write your own [user defined rules](user_defined_rules.md).
 - **Full unicode support:** Lint your Russian, Chinese or Emoji commit messages with ease!
 - **Production-ready:** Gitlint checks a lot of the boxes you're looking for: actively maintained, high unit test coverage, integration tests,
   python code standards (pep8, pylint), good documentation, widely used, proven track record.

## Getting Started
### Installation
```sh
# Pip is recommended to install the latest version
pip install gitlint

# Alternative: by default, gitlint is installed with pinned dependencies. 
# To install gitlint with looser dependency requirements, only install gitlint-core.
pip install gitlint-core

# Community maintained packages:
brew install gitlint       # Homebrew (macOS)
sudo port install gitlint  # Macports (macOS)
apt-get install gitlint    # Ubuntu
# Other package managers, see https://repology.org/project/gitlint/versions

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

# Ignore any data sent to gitlint via stdin
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
  --staged                 Read staged commit meta-info from the local
                           repository.
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
        args: [--contrib=CT1, --msg-filename]
```

!!! important

    You need to add `--msg-filename` at the end of your custom `args` list as the gitlint-hook will fail otherwise.


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

## Linting specific commits

Gitlint allows users to lint a specific commit:
```sh
gitlint --commit 019cf40580a471a3958d3c346aa8bfd265fe5e16
gitlint --commit 019cf40 # short SHAs work too
```

You can also lint multiple commits at once like so:

```sh
# Lint a specific commit range:
gitlint --commits "019cf40...d6bc75a"
# You can also use git's special references:
gitlint --commits "origin..HEAD"

# You can also pass multiple, comma separated commit hashes:
gitlint --commits 019cf40,c50eb150,d6bc75a
```

The `--commits` flag takes a **single** refspec argument or commit range. Basically, any range that is understood
by [git rev-list](https://git-scm.com/docs/git-rev-list) as a single argument will work.

Alternatively, you can pass `--commits` a comma-separated list of commit hashes (both short and full-length SHAs work).
Gitlint will lint these in the order you passed.

For cases where the `--commits` option doesn't provide the flexibility you need, you can always use a simple shell
script to lint an arbitrary set of commits, like shown in the example below.

```sh
#!/bin/sh

for commit in $(git rev-list my-branch); do
    echo "Commit $commit"
    gitlint --commit $commit
    echo "--------"
done
```

!!! note
    One downside to this approach is that you invoke gitlint once per commit vs. once per set of commits.
    This means you'll incur the gitlint startup time once per commit, making this approach rather slow if you want to
    lint a large set of commits. Always use `--commits` if you can to avoid this performance penalty.


## Merge, fixup, squash and revert commits
_Introduced in gitlint v0.7.0 (merge), v0.9.0 (fixup, squash), v0.13.0 (revert) and v0.18.0 (fixup=amend)_

**Gitlint ignores merge, revert, fixup, and squash commits by default.**

For merge and revert commits, the rationale for ignoring them is
that most users keep git's default messages for these commits (i.e *Merge/Revert "[original commit message]"*).
Often times these commit messages are also auto-generated through tools like github.
These default/auto-generated commit messages tend to cause gitlint violations.
For example, a common case is that *"Merge:"* being auto-prepended triggers a
[title-max-length](rules.md#t1-title-max-length) violation. Most users don't want this, so we disable linting
on Merge and Revert commits by default.

For [squash](https://git-scm.com/docs/git-commit#git-commit---squashltcommitgt) and [fixup](https://git-scm.com/docs/git-commit#git-commit---fixupltcommitgt) (including [fixup=amend](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---fixupamendrewordltcommitgt)) commits, the rationale is that these are temporary
commits that will be squashed into a different commit, and hence the commit messages for these commits are very
short-lived and not intended to make it into the final commit history. In addition, by prepending *"fixup!"*,
*"amend!"* or *"squash!"* to your commit message, certain gitlint rules might be violated
(e.g. [title-max-length](rules.md#t1-title-max-length)) which is often undesirable.

In case you *do* want to lint these commit messages, you can disable this behavior by setting the
general `ignore-merge-commits`, `ignore-revert-commits`,  `ignore-fixup-commits`, `ignore-fixup-amend-commits` or
`ignore-squash-commits` option to `false`
[using one of the various ways to configure gitlint](configuration.md).

## Ignoring commits

You can configure gitlint to ignore specific commits or parts of a commit.

One way to do this, is by [adding a gitlint-ignore line to your commit message](configuration.md#commit-specific-config).

If you have a case where you want to ignore a certain type of commits all-together, you can
use gitlint's *ignore* rules.
Here's a few examples snippets from a `.gitlint` file:

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

[ignore-by-author-name]
# Match commits by author name (e.g. ignore all rules when a commit is made by dependabot)
regex=dependabot
ignore=all
```

If you just want to ignore certain lines in a commit, you can do that using the
[ignore-body-lines](rules.md#i3-ignore-body-lines) rule.

```ini
# Ignore all lines that start with 'Co-Authored-By'
[ignore-body-lines]
regex=^Co-Authored-By
```

!!! warning

    When ignoring specific lines, gitlint will no longer be aware of them while applying other rules.
    This can sometimes be confusing for end-users, especially as line numbers of violations will typically no longer
    match line numbers in the original commit message. Make sure to educate your users accordingly.

!!! note

    If you want to implement more complex ignore rules according to your own logic, you can do so using [user-defined
    configuration rules](user_defined_rules.md#configuration-rules).

## Named Rules

Introduced in gitlint v0.14.0

Named rules allow you to have multiple of the same rules active at the same time, which allows you to
enforce the same rule multiple times but with different options. Named rules are so-called because they require an
additional unique identifier (i.e. the rule *name*) during configuration.

!!! warning

    Named rules is an advanced topic. It's easy to make mistakes by defining conflicting instances of the same rule.
    For example, by defining 2 `body-max-line-length` rules with different `line-length` options, you obviously create
    a conflicting situation. Gitlint does not do any resolution of such conflicts, it's up to you to make sure
    any configuration is non-conflicting. So caution advised!
    
Defining a named rule is easy, for example using your `.gitlint` file:

```ini
# By adding the following section, you will add a second instance of the
# title-must-not-contain-word (T5) rule (in addition to the one that is enabled
# by default) with the name 'extra-words'.
[title-must-not-contain-word:extra-words]
words=foo,bar

# So the generic form is
# [<rule-id-or-name>:<your-chosen-name>]
# Another example, referencing the rule type by id
[T5:more-words]
words=hur,dur

# You can add as many additional rules and you can name them whatever you want
# The only requirement is that names cannot contain whitespace or colons (:)
[title-must-not-contain-word:This-Can_Be*Whatever$YouWant]
words=wonderwoman,batman,power ranger
```

When executing gitlint, you will see the violations from the default `title-must-not-contain-word (T5)` rule, as well as
the violations caused by the additional Named Rules.

```sh
$ gitlint 
1: T5 Title contains the word 'WIP' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:This-Can_Be*Whatever$YouWant Title contains the word 'wonderwoman' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:extra-words Title contains the word 'foo' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:extra-words Title contains the word 'bar' (case-insensitive): "WIP: foo wonderwoman hur bar"
1: T5:more-words Title contains the word 'hur' (case-insensitive): "WIP: foo wonderwoman hur bar"
```

Named rules are further treated identical to all other rules in gitlint:

- You can reference them by their full name, when e.g. adding them to your `ignore` configuration
```ini
# .gitlint file example
[general]
ignore=T5:more-words,title-must-not-contain-word:extra-words
```

- You can use them to instantiate multiple of the same [user-defined rule](user_defined_rules.md)
- You can configure them using [any of the ways you can configure regular gitlint rules](configuration.md)


## Exit codes
Gitlint uses the exit code as a simple way to indicate the number of violations found.
Some exit codes are used to indicate special errors as indicated in the table below.

Because of these special error codes and the fact that
[bash only supports exit codes between 0 and 255](http://tldp.org/LDP/abs/html/exitcodes.html), the maximum number
of violations counted by the exit code is 252. Note that gitlint does not have a limit on the number of violations
it can detect, it will just always return with exit code 252 when the number of violations is greater than or equal
to 252.

| Exit Code | Description                                |
| --------- | ------------------------------------------ |
| 253       | Wrong invocation of the `gitlint` command. |
| 254       | Something went wrong when invoking git.    |
| 255       | Invalid gitlint configuration              |
