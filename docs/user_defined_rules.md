# User Defined Rules
_Introduced in gitlint v0.8.0_

Gitlint supports the concept of **user-defined** rules: the ability for users to write their own custom rules in python.

In a nutshell, use `--extra-path /home/joe/myextensions` to point gitlint to a `myextensions` directory where it will search
for python files containing gitlint rule classes. You can also specify a single python module, ie
`--extra-path /home/joe/my_rules.py`.

```sh
cat examples/commit-message-1 | gitlint --extra-path examples/
# Example output of a user-defined Signed-off-by rule
1: UC2 Body does not contain a 'Signed-off-by Line'
# other violations were removed for brevity
```

The `SignedOffBy` user-defined `CommitRule` was discovered by gitlint when it scanned
[examples/gitlint/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_commit_rules.py),
which is part of the examples directory that was passed via `--extra-path`:

```python
# -*- coding: utf-8 -*-
from gitlint.rules import CommitRule, RuleViolation

class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit contains a "Signed-off-by" line.
    We keep things simple here and just check whether the commit body contains a
    line that starts with "Signed-off-by".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id, we recommend starting with UC
    # (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        self.log.debug("SignedOffBy: This will be visible when running `gitlint --debug`")

        for line in commit.message.body:
            if line.startswith("Signed-off-by"):
                return

        msg = "Body does not contain a 'Signed-off-by' line"
        return [RuleViolation(self.id, msg, line_nr=1)]
```

As always, `--extra-path` can also be set by adding it under the `[general]` section in your `.gitlint` file or using
[one of the other ways to configure gitlint](configuration.md).

If you want to check whether your rules are properly discovered by gitlint, you can use the `--debug` flag:

```sh
$ gitlint --debug --extra-path examples/
# [output cut for brevity]
  UC1: body-max-line-count
     body-max-line-count=3
  UC2: body-requires-signed-off-by
  UL1: title-no-special-chars
     special-chars=['$', '^', '%', '@', '!', '*', '(', ')']
```

!!! Note
    In most cases it's really the easiest to just copy an example from the
    [examples](https://github.com/jorisroovers/gitlint/tree/main/examples) directory and modify it to your needs.
    The remainder of this page contains the technical details, mostly for reference.

## Line and Commit Rules
The `SignedOffBy` class above was an example of a user-defined `CommitRule`. Commit rules are gitlint rules that
act on the entire commit at once. Once the rules are discovered, gitlint will automatically take care of applying them
to the entire commit. This happens exactly once per commit.

A `CommitRule` contrasts with a `LineRule`
(see e.g.: [examples/my_line_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_line_rules.py))
in that a `CommitRule` is only applied once on an entire commit while a `LineRule` is applied for every line in the commit
(you can also apply it once to the title using a `target` - see the examples section below).

The benefit of a commit rule is that it allows commit rules to implement more complex checks that span multiple lines and/or checks
that should only be done once per commit.

While every `LineRule` can be implemented as a `CommitRule`, it's usually easier and more concise to go with a `LineRule` if
that fits your needs.

### Examples

In terms of code, writing your own `CommitRule` or `LineRule` is very similar.
The only 2 differences between a `CommitRule` and a `LineRule` are the parameters of the `validate(...)` method and the extra
`target` attribute that `LineRule` requires.

Consider the following `CommitRule` that can be found in [examples/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_commit_rules.py):

```python
# -*- coding: utf-8 -*-
from gitlint.rules import CommitRule, RuleViolation

class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit contains a "Signed-off-by" line.
    We keep things simple here and just check whether the commit body contains a
    line that starts with "Signed-off-by".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id, we recommend starting with UC
    # (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        self.log.debug("SignedOffBy: This will be visible when running `gitlint --debug`")

        for line in commit.message.body:
            if line.startswith("Signed-off-by"):
                return

        msg = "Body does not contain a 'Signed-off-by' line"
        return [RuleViolation(self.id, msg, line_nr=1)]
```
Note the use of the `name` and `id` class attributes and the `validate(...)` method taking a single `commit` parameter.

Contrast this with the following `LineRule` that can be found in [examples/my_line_rules.py](https://github.com/jorisroovers/gitlint/blob/main/examples/my_line_rules.py):

```python
# -*- coding: utf-8 -*-
from gitlint.rules import LineRule, RuleViolation, CommitMessageTitle
from gitlint.options import ListOption

class SpecialChars(LineRule):
    """ This rule will enforce that the commit message title does not contai
        any of the following characters:
        $^%@!*() """

    # A rule MUST have a human friendly name
    name = "title-no-special-chars"

    # A rule MUST have a *unique* id, we recommend starting with UL
    # for User-defined Line-rule), but this can really be anything.
    id = "UL1"

    # A line-rule MUST have a target (not required for CommitRules).
    target = CommitMessageTitle

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [ListOption('special-chars', ['$', '^', '%', '@', '!', '*', '(', ')'],
                               "Comma separated list of characters that should not occur in the title")]

    def validate(self, line, _commit):
        self.log.debug("SpecialChars: This will be visible when running `gitlint --debug`")

        violations = []
        # options can be accessed by looking them up by their name in self.options
        for char in self.options['special-chars'].value:
            if char in line:
                msg = f"Title contains the special character '{char}'"
                violation = RuleViolation(self.id, msg, line)
                violations.append(violation)

        return violations

```

Note the following 2 differences:

- **extra `target` class attribute**: in this example set to `CommitMessageTitle`  indicating that this `LineRule`
should only be applied once to the commit message title. The alternative value for `target` is `CommitMessageBody`,
 in which case gitlint will apply
your rule to **every** line in the commit message body.
- **`validate(...)` takes 2 parameters**: Line rules get the `line` against which they are applied as the first parameter and
the `commit` object of which the line is part of as second.

In addition, you probably also noticed the extra `options_spec` class attribute which allows you to make your rules configurable.
Options are not unique to `LineRule`s, they can also be used by `CommitRule`s and are further explained in the
[Options](user_defined_rules.md#options) section below.


## The commit object
Both `CommitRule`s and `LineRule`s take a `commit` object in their `validate(...)` methods.
The table below outlines the various attributes of that commit object that can be used during validation.


Property                       | Type           | Description
-------------------------------| ---------------|-------------------
commit.message                 | object         | Python object representing the commit message
commit.message.original        | string         | Original commit message as returned by git
commit.message.full            | string         | Full commit message, with comments (lines starting with #) removed.
commit.message.title           | string         | Title/subject of the commit message: the first line
commit.message.body            | string[]       | List of lines in the body of the commit message (i.e. starting from the second line)
commit.author_name             | string         | Name of the author, result of `git log --pretty=%aN`
commit.author_email            | string         | Email of the author, result of `git log --pretty=%aE`
commit.date                    | datetime       | Python `datetime` object representing the time of commit
commit.is_merge_commit         | boolean        | Boolean indicating whether the commit is a merge commit or not.
commit.is_revert_commit        | boolean        | Boolean indicating whether the commit is a revert commit or not.
commit.is_fixup_commit         | boolean        | Boolean indicating whether the commit is a fixup commit or not.
commit.is_fixup_amend_commit   | boolean        | Boolean indicating whether the commit is a (fixup) amend commit or not.
commit.is_squash_commit        | boolean        | Boolean indicating whether the commit is a squash commit or not.
commit.parents                 | string[]       | List of parent commit `sha`s (only for merge commits).
commit.changed_files           | string[]       | List of files changed in the commit (relative paths).
commit.branches                | string[]       | List of branch names the commit is part of
commit.context                 | object         | Object pointing to the bigger git context that the commit is part of
commit.context.current_branch  | string         | Name of the currently active branch (of local repo)
commit.context.repository_path | string         | Absolute path pointing to the git repository being linted
commit.context.commits         | object[]       | List of commits gitlint is acting on, NOT all commits in the repo.

## Violations
In order to let gitlint know that there is a violation in the commit being linted, users should have the `validate(...)`
method in their rules return a list of `RuleViolation`s.

!!! important
    The `validate(...)` method doesn't always need to return a list, you can just skip the return statement in case there are no violations.
    However, in case of a single violation, validate should return a **list** with a single item.

The `RuleViolation` class has the following generic signature:

```python
RuleViolation(rule_id, message, content=None, line_nr=None):
```
With the parameters meaning the following:

Parameter     | Type    |  Description
--------------|---------|--------------------------------
rule_id       | string  | Rule's unique string id
message       | string  | Short description of the violation
content       | string  | (optional) the violating part of commit or line
line_nr       | int     | (optional) line number in the commit message where the violation occurs. **Automatically set to the correct line number for `LineRule`s if not set explicitly.**

A typical `validate(...)` implementation for a `CommitRule` would then be as follows:
```python
def validate(self, commit)
    for line_nr, line in commit.message.body:
        if "Jon Snow" in line:
            # we add 1 to the line_nr because we offset the title which is on the first line
            return [RuleViolation(self.id, "Commit message has the words 'Jon Snow' in it", line, line_nr + 1)]
    return []
```

The parameters of this `RuleViolation` can be directly mapped onto gitlint's output as follows:

![How Rule violations map to gitlint output](images/RuleViolation.png)

## Options

In order to make your own rules configurable, you can add an optional `options_spec` attribute to your rule class
(supported for both `LineRule` and `CommitRule`).

```python
# -*- coding: utf-8 -*-
from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption

class BodyMaxLineCount(CommitRule):
    # A rule MUST have a human friendly name
    name = "body-max-line-count"

    # A rule MUST have a *unique* id, we recommend starting with UC (for
    # User-defined Commit-rule).
    id = "UC1"

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [IntOption('max-line-count', 3, "Maximum body line count")]

    def validate(self, commit):
        line_count = len(commit.message.body)
        max_line_count = self.options['max-line-count'].value
        if line_count > max_line_count:
            message = f"Body contains too many lines ({line_count} > {max_line_count})"
            return [RuleViolation(self.id, message, line_nr=1)]
```


By using `options_spec`, you make your option available to be configured through a `.gitlint` file
or one of the [other ways to configure gitlint](configuration.md). Gitlint automatically takes care of the parsing and input validation.

For example, to change the value of the `max-line-count` option, add the following to your `.gitlint` file:
```ini
[body-max-line-count]
body-max-line-count=1
```

As `options_spec` is a list, you can obviously have multiple options per rule. The general signature of an option is:
`Option(name, default_value, description)`.

Gitlint supports a variety of different option types, all can be imported from `gitlint.options`:

Option Class      | Use for
------------------|--------------
`StrOption `      | Strings
`IntOption`       | Integers. `IntOption` takes an optional `allow_negative` parameter if you want to allow negative integers.
`BoolOption`      | Booleans. Valid values: `true`, `false`. Case-insensitive.
`ListOption`      | List of strings. Comma separated.
`PathOption`      | Directory or file path. Takes an optional `type` parameter for specifying path type (`file`, `dir` (=default) or `both`).
`RegexOption`     | String representing a [Python-style regex](https://docs.python.org/library/re.html) - compiled and validated before rules are applied.

!!! note
    Gitlint currently does not support options for all possible types (e.g. float, list of int, etc).
    [We could use a hand getting those implemented](contributing.md)!


## Configuration Rules

_Introduced in gitlint v0.14.0_

Configuration rules are special rules that are applied once per commit and *BEFORE* any other rules are run.
Configuration rules are meant to dynamically change gitlint's configuration and/or the commit that is about to be
linted.
A typically use-case for this is when you want to modifying gitlint's behavior for all rules against a commit matching
specific circumstances.

!!! warning
    Configuration rules can drastically change the way gitlint behaves and are typically only needed for more advanced
    use-cases. We recommend you double check:

    1. Whether gitlint already supports your use-case out-of-the-box (special call-out for [ignore rules](rules.md#i1-ignore-by-title) which allow you to ignore (parts) of your commit message).
    2. Whether there's a [Contrib Rule](contrib_rules.md) that implements your use-case.
    3. Whether you can implement your use-case using a regular Commit or Line user-defined rule (see above).


As with other user-defined rules, the easiest way to get started is by copying [`my_configuration.py` from the examples directory](https://github.com/jorisroovers/gitlint/tree/main/examples/my_configuration_rules.py) and modifying it to fit your need.

```python
# -*- coding: utf-8 -*-
from gitlint.rules import ConfigurationRule
from gitlint.options import IntOption

class ReleaseConfigurationRule(ConfigurationRule):
    """
    This rule will modify gitlint's behavior for Release Commits.

    This example might not be the most realistic for a real-world scenario,
    but is meant to give an overview of what's possible.
    """

    # A rule MUST have a human friendly name
    name = "release-configuration-rule"

    # A rule MUST have a *unique* id, we recommend starting with UCR
    # (for User-defined Configuration-Rule), but this can really be anything.
    id = "UCR1"

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [IntOption('custom-verbosity', 2, "Gitlint verbosity for release commits")]

    def apply(self, config, commit):
        self.log.debug("ReleaseConfigurationRule: This will be visible when running `gitlint --debug`")

        # If the commit title starts with 'Release', we want to modify
        # how all subsequent rules interpret that commit
        if commit.message.title.startswith("Release"):

            # If your Release commit messages are auto-generated, the
            # body might contain trailing whitespace. Let's ignore that
            config.ignore.append("body-trailing-whitespace")

            # Similarly, the body lines might exceed 80 chars,
            # let's set gitlint's limit to 200
            # To set rule options use:
            # config.set_rule_option(<rule-name>, <rule-option>, <value>)
            config.set_rule_option("body-max-line-length", "line-length", 200)

            # For kicks, let's set gitlint's verbosity to 2
            # To set general options use
            # config.set_general_option(<general-option>, <value>)
            config.set_general_option("verbosity", 2)
            # We can also use custom options to make this configurable
            config.set_general_option("verbosity", self.options['custom-verbosity'].value)

            # Strip any lines starting with $ from the commit message
            # (this only affects how gitlint sees your commit message, it does
            # NOT modify your actual commit in git)
            commit.message.body = [line for line in commit.message.body if not line.startswith("$")]

            # You can add any extra properties you want to the commit object,
            # these will be available later on in all rules.
            commit.my_property = "This is my property"
```

For all available properties and methods on the `config` object, have a look at the
[LintConfig class](https://github.com/jorisroovers/gitlint/blob/main/gitlint-core/gitlint/config.py). Please do not use any
properties or methods starting with an underscore, as those are subject to change.


## Rule requirements

As long as you stick with simple rules that are similar to the sample user-defined rules (see the
[examples](https://github.com/jorisroovers/gitlint/blob/main/examples/my_commit_rules.py) directory), gitlint
should be able to discover and execute them. While clearly you can run any python code you want in your rules,
you might run into some issues if you don't follow the conventions that gitlint requires.

While the [rule finding source-code](https://github.com/jorisroovers/gitlint/blob/main/gitlint-core/gitlint/rule_finder.py) is the
ultimate source of truth, here are some of the requirements that gitlint enforces.

### Rule class requirements

- Rules **must** extend from  `LineRule`, `CommitRule` or `ConfigurationRule`
- Rule classes **must** have `id` and `name` string attributes. The `options_spec` is optional,
  but if set, it **must** be a list of gitlint Options.
- `CommitRule` and `LineRule` classes **must** have a `validate` method.
- In case of a `CommitRule`, `validate`  **must** take a single `commit` parameter.
- In case of `LineRule`, `validate` **must** take `line` and `commit` as first and second parameters.
- `ConfigurationRule` classes **must** have an `apply` method that take `config` and `commit` as first and second parameters.
- LineRule classes **must** have a `target` class attributes that is set to either `CommitMessageTitle` or `CommitMessageBody`.
- User Rule id's **cannot** start with `R`, `T`, `B`, `M` or `I` as these rule ids are reserved for gitlint itself.
- Rules **should** have a case-insensitive unique id as only one rule can exist with a given id. While gitlint does not
  enforce this, having multiple rules with the same id might lead to unexpected or undeterministic behavior.

### extra-path requirements
- If  `extra-path` is a directory, it does **not** need to be a proper python package, i.e. it doesn't require an `__init__.py` file.
- Python files containing user-defined rules must have a `.py` extension. Files with a different extension will be ignored.
- The `extra-path` will be searched non-recursively, i.e. all rule classes must be present at the top level `extra-path` directory.
- User rule classes must be defined in the modules that are part of `extra-path`, rules that are imported from outside the `extra-path` will be ignored.
