# Configuration
Gitlint can be configured through different means.

## The .gitlint file
You can modify gitlint's behavior by adding a `.gitlint` file to your git repository.

Generate a default `.gitlint` config file by running:
```sh
gitlint generate-config
```
You can also use a different config file like so:

```sh
gitlint --config myconfigfile.ini 
```

The block below shows a sample `.gitlint` file. Details about rule config options can be found on the
[Rules](rules.md) page, details about the `[general]` section can be found in the
[General Configuration](configuration.md#general-configuration) section of this page.

```ini
# Edit this file as you like.
#
# All these sections are optional. Each section with the exception of [general] represents
# one rule and each key in it is an option for that specific rule.
#
# Rules and sections can be referenced by their full name or by id. For example
# section "[body-max-line-length]" could also be written as "[B1]". Full section names are
# used in here for clarity.
# Rule reference documentation: http://jorisroovers.github.io/gitlint/rules/
#
# Use 'gitlint generate-config' to generate a config file with all possible options
[general]
# Ignore certain rules (comma-separated list), you can reference them by their
# id or by their full name
ignore=title-trailing-punctuation, T3

# verbosity should be a value between 1 and 3, the commandline -v flags take
# precedence over this
verbosity = 2

# By default gitlint will ignore merge, revert, fixup, fixup=amend, and squash commits.
ignore-merge-commits=true
ignore-revert-commits=true
ignore-fixup-commits=true
ignore-fixup-amend-commits=true
ignore-squash-commits=true

# Ignore any data sent to gitlint via stdin
ignore-stdin=true

# Fetch additional meta-data from the local repository when manually passing a 
# commit message to gitlint via stdin or --commit-msg. Disabled by default.
staged=true

# Hard fail when the target commit range is empty. Note that gitlint will
# already fail by default on invalid commit ranges. This option is specifically
# to tell gitlint to fail on *valid but empty* commit ranges.
# Disabled by default.
fail-without-commits=true

# Enable debug mode (prints more output). Disabled by default.
debug=true

# Enable community contributed rules
# See http://jorisroovers.github.io/gitlint/contrib_rules for details
contrib=contrib-title-conventional-commits,CC1

# Set the extra-path where gitlint will search for user defined rules
# See http://jorisroovers.github.io/gitlint/user_defined_rules for details
extra-path=examples/

# This is an example of how to configure the "title-max-length" rule and
# set the line-length it enforces to 80
[title-max-length]
line-length=80

# Conversely, you can also enforce minimal length of a title with the
# "title-min-length" rule:
[title-min-length]
min-length=5

[title-must-not-contain-word]
# Comma-separated list of words that should not occur in the title. Matching is case
# insensitive. It's fine if the keyword occurs as part of a larger word (so "WIPING"
# will not cause a violation, but "WIP: my title" will.
words=wip

[title-match-regex]
# python like regex (https://docs.python.org/3/library/re.html) that the
# commit-msg title must be matched to.
# Note that the regex can contradict with other rules if not used correctly
# (e.g. title-must-not-contain-word).
regex=^US[0-9]*

[body-max-line-length]
line-length=120

[body-min-length]
min-length=5

[body-is-missing]
# Whether to ignore this rule on merge commits (which typically only have a title)
# default = True
ignore-merge-commits=false

[body-changed-file-mention]
# List of files that need to be explicitly mentioned in the body when they are changed
# This is useful for when developers often erroneously edit certain files or git submodules.
# By specifying this rule, developers can only change the file when they explicitly
# reference it in the commit message.
files=gitlint-core/gitlint/rules.py,README.md

[body-match-regex]
# python-style regex that the commit-msg body must match.
# E.g. body must end in My-Commit-Tag: foo
regex=My-Commit-Tag: foo$

[author-valid-email]
# python like regex (https://docs.python.org/3/library/re.html) that the
# commit author email address should be matched to
# E.g.: For example, use the following regex if you only want to allow email
# addresses from foo.com
regex=[^@]+@foo.com

[ignore-by-title]
# Ignore certain rules for commits of which the title matches a regex
# E.g. Match commit titles that start with "Release"
regex=^Release(.*)

# Ignore certain rules, you can reference them by their id or by their full name
# Use 'all' to ignore all rules
ignore=T1,body-min-length

[ignore-by-body]
# Ignore certain rules for commits of which the body has a line that matches a regex
# E.g. Match bodies that have a line that that contain "release"
regex=(.*)release(.*)
#
# Ignore certain rules, you can reference them by their id or by their full name
# Use 'all' to ignore all rules
ignore=T1,body-min-length

[ignore-body-lines]
# Ignore certain lines in a commit body that match a regex.
# E.g. Ignore all lines that start with 'Co-Authored-By'
regex=^Co-Authored-By

[ignore-by-author-name]
# Ignore certain rules for commits of which the author name matches a regex
# E.g. Match commits made by dependabot
regex=(.*)dependabot(.*)

# Ignore certain rules, you can reference them by their id or by their full name
# Use 'all' to ignore all rules
ignore=T1,body-min-length

# This is a contrib rule - a community contributed rule. These are disabled by default.
# You need to explicitly enable them one-by-one by adding them to the "contrib" option
# under [general] section above.
[contrib-title-conventional-commits]
# Specify allowed commit types. For details see: https://www.conventionalcommits.org/
types = bugfix,user-story,epic
```

## Commandline config

You can also use one or more `-c` flags like so:

```
$ gitlint -c general.verbosity=2 -c title-max-length.line-length=80 -c B1.line-length=100
```
The generic config flag format is `-c <rule>.<option>=<value>` and supports all the same rules and options which
you can also use in a `.gitlint` config file.

## Commit specific config

You can also configure gitlint by adding specific lines to your commit message.
For now, we only support ignoring commits by adding `gitlint-ignore: all` to the commit
message like so:

```
WIP: This is my commit message

I want gitlint to ignore this entire commit message.
gitlint-ignore: all
```

`gitlint-ignore: all` can occur on any line, as long as it is at the start of the line.

You can also specify specific rules to be ignored as follows: 
```
WIP: This is my commit message

I want gitlint to ignore this entire commit message.
gitlint-ignore: T1, body-hard-tab
```



## Configuration precedence
gitlint configuration is applied in the following order of precedence:

1. Commit specific config (e.g.: `gitlint-ignore: all` in the commit message)
2. Configuration Rules (e.g.: [ignore-by-title](/rules/#i1-ignore-by-title))
3. Commandline convenience flags (e.g.:  `-vv`, `--silent`, `--ignore`)
4. Environment variables (e.g.: `GITLINT_VERBOSITY=3`)
5. Commandline configuration flags (e.g.: `-c title-max-length=123`)
6. Configuration file (local `.gitlint` file, or file specified using `-C`/`--config`)
7. Default gitlint config

## General Options
Below we outline all configuration options that modify gitlint's overall behavior. These options can be specified
using commandline flags or in `[general]` section in a `.gitlint` configuration file.

### silent

Enable silent mode (no output). Use [exit](index.md#exit-codes) code to determine result.

Default value  |  gitlint version | commandline flag  | environment variable
---------------|------------------|-------------------|-----------------------
`False`        | >= 0.1.0         | `--silent`        | `GITLINT_SILENT`

#### Examples
```sh
# CLI
gitlint --silent
GITLINT_SILENT=1 gitlint  # using env variable
```

### verbosity

Amount of output gitlint will show when printing errors.

Default value  |  gitlint version | commandline flag  | environment variable 
---------------|------------------|-------------------|-----------------------
3              | >= 0.1.0         | `-v`              | `GITLINT_VERBOSITY`


#### Examples
```sh
# CLI
gitlint -vvv                   # default     (level 3)
gitlint -vv                    # less output (level 2)
gitlint -v                     # even less   (level 1)
gitlint --silent               # no output   (level 0)
gitlint -c general.verbosity=1 # Set specific level
gitlint -c general.verbosity=0 # Same as --silent
GITLINT_VERBOSITY=2 gitlint    # using env variable
```
```ini
# .gitlint
[general]
verbosity=2
```

### ignore

Comma separated list of rules to ignore (by name or id).

Default value              |  gitlint version | commandline flag  | environment variable   
---------------------------|------------------|-------------------|-----------------------
 [] (=empty list)          | >= 0.1.0         | `--ignore`        | `GITLINT_IGNORE`

#### Examples
```sh
# CLI
gitlint --ignore=body-min-length              # ignore single rule
gitlint --ignore=T1,body-min-length           # ignore multiple rule
gitlint -c general.ignore=T1,body-min-length  # different way of doing the same
GITLINT_IGNORE=T1,body-min-length gitlint     # using env variable
```
```ini
#.gitlint
[general]
ignore=T1,body-min-length
```

### debug

Enable debugging output.

Default value  |  gitlint version | commandline flag  | environment variable   
---------------|------------------|-------------------|-----------------------
 false         | >= 0.7.1         | `--debug`         | `GITLINT_DEBUG`

#### Examples
```sh
# CLI
gitlint --debug
GITLINT_DEBUG=1 gitlint # using env variable
# --debug is special, the following does NOT work
# gitlint -c general.debug=true
```

### target

Target git repository gitlint should be linting against.

Default value              |  gitlint version | commandline flag  | environment variable   
---------------------------|------------------|-------------------|-----------------------
(empty)                    | >= 0.8.0         | `--target`        | `GITLINT_TARGET`

#### Examples
```sh
# CLI
gitlint --target=/home/joe/myrepo/
gitlint -c general.target=/home/joe/myrepo/  # different way of doing the same
GITLINT_TARGET=/home/joe/myrepo/ gitlint     # using env variable
```
```ini
#.gitlint
[general]
target=/home/joe/myrepo/
```
### config

Path where gitlint looks for a config file.

Default value              |  gitlint version | commandline flag  | environment variable   
---------------------------|------------------|-------------------|-----------------------
`.gitlint`                 | >= 0.1.0         | `--config`        | `GITLINT_CONFIG`

#### Examples
```sh
gitlint --config=/home/joe/gitlint.ini
gitlint -C /home/joe/gitlint.ini      # different way of doing the same
GITLINT_CONFIG=/home/joe/gitlint.ini  # using env variable
```

### extra-path

Path where gitlint looks for [user-defined rules](user_defined_rules.md).

Default value              |  gitlint version | commandline flag  | environment variable   
---------------------------|------------------|-------------------|-----------------------
 (empty)                   | >= 0.8.0         | `--extra-path`    | `GITLINT_EXTRA_PATH`

#### Examples
```sh
# CLI
gitlint --extra-path=/home/joe/rules/
gitlint -c general.extra-path=/home/joe/rules/  # different way of doing the same
GITLINT_EXTRA_PATH=/home/joe/rules/ gitlint     # using env variable
```
```ini
#.gitlint
[general]
extra-path=/home/joe/rules/
```

### contrib

Comma-separated list of [Contrib rules](contrib_rules) to enable (by name or id).

Default value              |  gitlint version | commandline flag  | environment variable   
---------------------------|------------------|-------------------|-----------------------
 (empty)                   | >= 0.12.0        | `--contrib`       | `GITLINT_CONTRIB`

#### Examples
```sh
# CLI
gitlint --contrib=contrib-title-conventional-commits,CC1
# different way of doing the same
gitlint -c general.contrib=contrib-title-conventional-commits,CC1
# using env variable
GITLINT_CONTRIB=contrib-title-conventional-commits,CC1 gitlint   
```
```ini
#.gitlint
[general]
contrib=contrib-title-conventional-commits,CC1
```

### staged

Fetch additional meta-data from the local repository when manually passing a commit message to gitlint via stdin or `--commit-msg`.

Default value  |  gitlint version | commandline flag  | environment variable   
---------------|------------------|-------------------|-----------------------
 false         | >= 0.13.0        | `--staged`        | `GITLINT_STAGED`

#### Examples
```sh
# CLI
gitlint --staged
gitlint -c general.staged=true # different way of doing the same
GITLINT_STAGED=1 gitlint       # using env variable
```
```ini
#.gitlint
[general]
staged=true
```

### fail-without-commits

Hard fail when the target commit range is empty. Note that gitlint will
already fail by default on invalid commit ranges. This option is specifically
to tell gitlint to fail on **valid but empty** commit ranges.

Default value  |  gitlint version | commandline flag  | environment variable   
---------------|------------------|---------------------------|-----------------------
 false         | >= 0.15.2        | `--fail-without-commits`  | `GITLINT_FAIL_WITHOUT_COMMITS`

#### Examples
```sh
# CLI
# The following will cause gitlint to hard fail (i.e. exit code > 0)
# since HEAD..HEAD is a valid but empty commit range. 
gitlint --fail-without-commits --commits HEAD..HEAD
GITLINT_FAIL_WITHOUT_COMMITS=1 gitlint       # using env variable
```
```ini
#.gitlint
[general]
fail-without-commits=true
```

### ignore-stdin

Ignore any stdin data. Sometimes useful when running gitlint in a CI server.

Default value  |  gitlint version | commandline flag  | environment variable   
---------------|------------------|-------------------|-----------------------
 false         | >= 0.12.0        | `--ignore-stdin`  | `GITLINT_IGNORE_STDIN`

#### Examples
```sh
# CLI
gitlint --ignore-stdin
gitlint -c general.ignore-stdin=true # different way of doing the same
GITLINT_IGNORE_STDIN=1 gitlint       # using env variable
```
```ini
#.gitlint
[general]
ignore-stdin=true
```

### ignore-merge-commits

Whether or not to ignore merge commits.

Default value  |  gitlint version | commandline flag  | environment variable  
---------------|------------------|-------------------|-----------------------
 true          | >= 0.7.0         | Not Available     | Not Available  

#### Examples
```sh
# CLI
gitlint -c general.ignore-merge-commits=false
```
```ini
#.gitlint
[general]
ignore-merge-commits=false
```

### ignore-revert-commits

Whether or not to ignore revert commits.

Default value  |  gitlint version | commandline flag  | environment variable   
---------------|------------------|-------------------|-----------------------
 true          | >= 0.13.0        | Not Available     | Not Available  

#### Examples
```sh
# CLI
gitlint -c general.ignore-revert-commits=false
```
```ini
#.gitlint
[general]
ignore-revert-commits=false
```

### ignore-fixup-commits

Whether or not to ignore [fixup](https://git-scm.com/docs/git-commit#git-commit---fixupltcommitgt) commits.

Default value  |  gitlint version | commandline flag  | environment variable  
---------------|------------------|-------------------|-----------------------
 true          | >= 0.9.0         | Not Available     | Not Available  

#### Examples
```sh
# CLI
gitlint -c general.ignore-fixup-commits=false
```
```ini
#.gitlint
[general]
ignore-fixup-commits=false
```

### ignore-fixup-amend-commits

Whether or not to ignore [fixup=amend](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---fixupamendrewordltcommitgt) commits.

Default value  |  gitlint version | commandline flag  | environment variable  
---------------|------------------|-------------------|-----------------------
 true          | >= 0.18.0        | Not Available     | Not Available  

#### Examples
```sh
# CLI
gitlint -c general.ignore-fixup-amend-commits=false
```
```ini
#.gitlint
[general]
ignore-fixup-amend-commits=false
```

### ignore-squash-commits

Whether or not to ignore [squash](https://git-scm.com/docs/git-commit#git-commit---squashltcommitgt) commits.

Default value  |  gitlint version | commandline flag  | environment variable 
---------------|------------------|-------------------|-----------------------
 true          | >= 0.9.0         | Not Available     | Not Available  

#### Examples
```sh
# CLI
gitlint -c general.ignore-squash-commits=false
```
```ini
#.gitlint
[general]
ignore-squash-commits=false
```