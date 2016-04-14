# Config files #
You can modify gitlint's behavior by adding a ```.gitlint``` file to your git repository.

Generate a default ```.gitlint``` config file by running:
```bash
gitlint generate-config
```
You can also use a different config file like so:

```bash
gitlint --config myconfigfile.ini 
```

The block below shows a sample ```.gitlint``` file. Details about rule config options can be found on the [Rules](rules.md) page.

```ini
# All these sections are optional, edit this file as you like.
[general]
ignore=title-trailing-punctuation, T3
# verbosity should be a value between 1 and 3, the commandline -v flags take precedence over
# this
verbosity = 2

[title-max-length]
line-length=20

[title-must-not-contain-word]
# Comma-separated list of words that should not occur in the title. Matching is case
# insensitive. It's fine if the keyword occurs as part of a larger word (so "WIPING"
# will not cause a violation, but "WIP: my title" will.
words=wip,title

[title-match-regex]
# python like regex (https://docs.python.org/2/library/re.html) that the
# commit-msg title must be matched to.
# Note that the regex can contradict with other rules if not used correctly
# (e.g. title-must-not-contain-word).
regex=^US[0-9]*

[B1]
# B1 = body-max-line-length
line-length=30

[body-min-length]
min-length=5

[body-is-missing]
# Whether to ignore this rule on merge commits (which typically only have a title)
# default = True
ignore-merge-commits=false

[body-changed-file-mention]
# List of files that need to be explicitly mentioned in the body when they are changed
# This is useful for when developers often erroneously edit certain files or git submodules.
# By specifying this rule, developers can only change the file when they explicitly reference
# it in the commit message.
files=gitlint/rules.py,README.md
```

# Commandline config #

You can also use one or more ```-c``` flags like so:

```
$ gitlint -c general.verbosity=2 -c title-max-length.line-length=80 -c B1.line-length=100
```
The generic config flag format is ```-c <rule>.<option>=<value>``` and supports all the same rules and options which 
you can also use in a ```.gitlint``` config file.

# Commit specific config #

You can also disable gitlint for specific commit messages by adding ```gitlint-ignore: all``` to the commit
message like so:

```
WIP: This is my commit message

I want gitlint to ignore this entire commit message.
gitlint-ignore: all
```

```gitlint-ignore: all``` can occur on any line, as long as it is at the start of the line. You can also specify
specific rules to be ignored as follows: ```gitlint-ignore: T1, body-hard-tab```.

## Configuration precedence ##
Configuring gitlint happens the following order of precedence:

1. Commit specific config (e.g.: ```gitlint-ignore: all``` in the commit message) 
2. Commandline convenience flags (e.g.:  ```-vv```, ```--silent```, ```--ignore```)
3. Commandline configuration flags (e.g.: ```-c title-max-length=123```)
4. Configuration file (local ```.gitlint``` file, or file specified using ```-C```/```--config```)
5. Default gitlint config
