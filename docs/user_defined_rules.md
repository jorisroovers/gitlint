# User Defined Rules
_Introduced in gitlint v0.8.0_

Gitlint supports the concept of user-defined rules: the ability for users to write their own custom rules in python.

In a nutshell, use ```--extra-path /home/joe/myextensions``` to point gitlint to a ```myextensions``` directory where it will search
for python files containing gitlint rule classes. You can also specify a single python module, ie
```--extra-path /home/joe/my_rules.py```.

```bash
cat examples/commit-message-1 | gitlint --extra-path examples/
1: UC2 Body does not contain a 'Signed-Off-By Line' # Example output of a user-defined Signed-Off-By rule
# other violations were removed for brevity
```

The SignedOffBy user-defined ```CommitRule``` was discovered by gitlint when it scanned
[examples/gitlint/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/master/examples/my_commit_rules.py),
which is part of the examples directory that was passed via ```--extra-path```:

```python
from gitlint.rules import CommitRule, RuleViolation

class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit contains a "Signed-Off-By" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-Off-By".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        for line in commit.message.body:
            if line.startswith("Signed-Off-By"):
                return

        return [RuleViolation(self.id, "Body does not contain a 'Signed-Off-By' line", line_nr=1)]
```

As always, ```--extra-path``` can also be set by adding it under the ```[general]``` section in your ```.gitlint``` file or using
[one of the other ways to configure gitlint](configuration.md).

If you want to check whether your rules are properly discovered by gitlint, you can use the ```--debug``` flag:

```bash
$ gitlint --debug --extra-path examples/
[output cut for brevity]
  UC1: body-max-line-count
     body-max-line-count=3
  UC2: body-requires-signed-off-by
  UL1: title-no-special-chars
     special-chars=['$', '^', '%', '@', '!', '*', '(', ')']
```

!!! Note
    In most cases it's really the easiest to just copy an example from the
    [examples](https://github.com/jorisroovers/gitlint/tree/master/examples) directory and modify it to your needs.
    The remainder of this page contains the technical details, mostly for reference.

## Line and Commit Rules ##
The ```SignedOffBy``` class above was an example of a user-defined ```CommitRule```. Commit rules are gitlint rules that
act on the entire commit at once. Once the rules are discovered, gitlint will automatically take care of applying them
to the entire commit. This happens exactly once per commit.

A ```CommitRule``` contrasts with a ```LineRule```
(see e.g.: [examples/my_line_rules.py](https://github.com/jorisroovers/gitlint/blob/master/examples/my_line_rules.py))
in that a ```CommitRule``` is only applied once on an entire commit while a ```LineRule``` is applied for every line in the commit
(you can also apply it once to the title using a ```target``` - see the examples section below).

The benefit of a commit rule is that it allows commit rules to implement more complex checks that span multiple lines and/or checks
that should only be done once per gitlint run.

While every ```LineRule``` can be implemented as a ```CommitRule```, it's usually easier and more concise to go with a ```LineRule``` if
that fits your needs.

### Examples ###

In terms of code, writing your own ```CommitRule``` or ```LineRule``` is very similar.
The only 2 differences between a ```CommitRule``` and a ```LineRule``` are the parameters of the ```validate(...)``` method and the extra
```target``` attribute that ```LineRule``` requires.

Consider the following ```CommitRule``` that can be found in [examples/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/master/examples/my_commit_rules.py):

```python
from gitlint.rules import CommitRule, RuleViolation

class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit contains a "Signed-Off-By" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-Off-By".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have a *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        for line in commit.message.body:
            if line.startswith("Signed-Off-By"):
                return []

        return [RuleViolation(self.id, "Body does not contain a 'Signed-Off-By Line'", line_nr=1)]
```
Note the use of the ```name``` and ```id``` class attributes and the ```validate(...)``` method taking a single ```commit``` parameter.

Contrast this with the following ```LineRule``` that can be found in [examples/my_line_rules.py](https://github.com/jorisroovers/gitlint/blob/master/examples/my_line_rules.py):

```python
from gitlint.rules import LineRule, RuleViolation, CommitMessageTitle
from gitlint.options import ListOption

class SpecialChars(LineRule):
    """ This rule will enforce that the commit message title does not contain any of the following characters:
        $^%@!*() """

    # A rule MUST have a human friendly name
    name = "title-no-special-chars"

    # A rule MUST have a *unique* id, we recommend starting with UL (for User-defined Line-rule), but this can
    # really be anything.
    id = "UL1"

    # A line-rule MUST have a target (not required for CommitRules).
    target = CommitMessageTitle

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [ListOption('special-chars', ['$', '^', '%', '@', '!', '*', '(', ')'],
                               "Comma separated list of characters that should not occur in the title")]

    def validate(self, line, commit):
        violations = []
        # options can be accessed by looking them up by their name in self.options
        for char in self.options['special-chars'].value:
            if char in line:
                violation = RuleViolation(self.id, "Title contains the special character '{}'".format(char), line)
                violations.append(violation)

        return violations
```

Note the following 2 differences:

- **extra ```target``` class attribute**: in this example set to ```CommitMessageTitle```  indicating that this ```LineRule```
should only be applied once to the commit message title. The alternative value for ```target``` is ```CommitMessageBody```,
 in which case gitlint will apply
your rule to every line in the commit message body.
- **```validate(...)``` takes 2 parameters**: Line rules get the ```line``` against which they are applied as the first parameter and
the ```commit``` object of which the line is part of as second.

In addition, you probably also noticed the extra ```options_spec``` class attribute which allows you to make your rules configurable.
Options are not unique to ```LineRule```s, they can also be used by ```CommitRule```s and are further explained in the
[Options](user_defined_rules.md#options) section below.


## The commit object ##
Both ```CommitRule```s and ```LineRule```s take a ```commit``` object in their ```validate(...)``` methods.
The table below outlines the various attributes of that commit object that can be used during validation.


commit attribute        | Type           | Description
------------------------| ---------------|-------------------
commit.message          | object         | Python object representing the commit message
commit.message.original | string         | Original commit message as returned by git
commit.message.full     | string         | Full commit message, with comments (lines starting with #) removed.
commit.message.title    | string         | Title/subject of the commit message: the first line
commit.message.body     | list of string | List of lines in the body of the commit message (i.e. starting from the second line)
commit.author_name      | string         | Name of the author, result of ```git log --pretty=%aN```
commit.author_email     | string         | Email of the author, result of ```git log --pretty=%aE```
commit.date             | datetime       | Python ```datetime``` object representing the time of commit
commit.is_merge_commit  | boolean        | Boolean indicating whether the commit is a merge commit or not.
commit.is_revert_commit | boolean        | Boolean indicating whether the commit is a revert commit or not.
commit.is_fixup_commit  | boolean        | Boolean indicating whether the commit is a fixup commit or not.
commit.is_squash_commit | boolean        | Boolean indicating whether the commit is a squash commit or not.
commit.parents          | list of string | List of parent commit ```sha```s (only for merge commits).
commit.changed_files    | list of string | List of files changed in the commit (relative paths).
commit.branches         | list of string | List of branch names the commit is part of
commit.context          | object         | Object pointing to the bigger git context that the commit is part of
commit.context.commits  | list of commit | List of commits in the git context. Note that this might only be the subset of commits that gitlint is acting on, not all commits in the repo.

## Violations ##
In order to let gitlint know that there is a violation in the commit being linted, users should have the ```validate(...)```
method in their rules return a list of ```RuleViolation```s.

!!! important
    The ```validate(...)``` method doesn't always need to return a list, you can just skip the return statement in case there are no violations.
    However, in case of a single violation, validate should return a **list** with a single item.

The ```RuleViolation``` class has the following generic signature:

```
RuleViolation(rule_id, message, content=None, line_nr=None):
```
With the parameters meaning the following:

Parameter     | Type    |  Description
--------------|---------|--------------------------------
rule_id       | string  | Rule's unique string id
message       | string  | Short description of the violation
content       | string  | (optional) the violating part of commit or line
line_nr       | int     | (optional) line number in the commit message where the violation occurs. **Automatically set to the correct line number for ```LineRule```s if not set explicitly.**

A typical ```validate(...)``` implementation for a ```CommitRule``` would then be as follows:
```python
def validate(self, commit)
    for line_nr, line in commit.message.body:
        if "Jon Snow" in line:
            # we add 1 to the line_nr because we offset the title which is on the first line
            return [RuleViolation(self.id, "Commit message has the words 'Jon Snow' in it", line, line_nr + 1)]
    return []
```

The parameters of this ```RuleViolation``` can be directly mapped onto gitlint's output as follows:

![How Rule violations map to gitlint output](images/RuleViolation.png)

## Options ##

In order to make your own rules configurable, you can add an optional ```options_spec``` attribute to your rule class
(supported for both ```LineRule``` and ```CommitRule```).

```python
from gitlint.rules import CommitRule, RuleViolation
from gitlint.options import IntOption

class BodyMaxLineCount(CommitRule):
    # A rule MUST have a human friendly name
    name = "body-max-line-count"

    # A rule MUST have a *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC1"

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [IntOption('max-line-count', 3, "Maximum body line count")]

    def validate(self, commit):
        line_count = len(commit.message.body)
        max_line_count = self.options['max-line-count'].value
        if line_count > max_line_count:
            message = "Body contains too many lines ({0} > {1})".format(line_count, max_line_count)
            return [RuleViolation(self.id, message, line_nr=1)]
```


By using ```options_spec```, you make your option available to be configured through a ```.gitlint``` file
or one of the [other ways to configure gitlint](configuration.md). Gitlint automatically takes care of the parsing and input validation.

For example, to change the value of the ```max-line-count``` option, add the following to your ```.gitlint``` file:
```ini
[body-max-line-count]
body-max-line-count=1
```

As ```options_spec``` is a list, you can obviously have multiple options per rule. The general signature of an option is:
```Option(name, default_value, description)```.

Gitlint supports a variety of different option types, all can be imported from ```gitlint.options```:

Option Class    | Use for
----------------|--------------
StrOption       | Strings
IntOption       | Integers. ```IntOption``` takes an optional ```allow_negative``` parameter if you want to allow negative integers.
BoolOption      | Booleans. Valid values: true, false. Case-insensitive.
ListOption      | List of strings. Comma separated.
PathOption      | Directory or file path. Takes an optional ```type``` parameter for specifying path type (```file```, ```dir``` (=default) or ```both```).

!!! note
    Gitlint currently does not support options for all possible types (e.g. float, filepath, list of int, etc).
    [We could use a hand getting those implemented](contributing.md)!


## Rule requirements ##

As long as you stick with simple rules that are similar to the sample user-defined rules (see the
[examples](https://github.com/jorisroovers/gitlint/blob/master/examples/my_commit_rules.py) directory), gitlint
should be able to discover and execute them. While clearly you can run any python code you want in your rules,
you might run into some issues if you don't follow the conventions that gitlint requires.

While the [rule finding source-code](https://github.com/jorisroovers/gitlint/blob/master/gitlint/user_rules.py) is the
ultimate source of truth, here are some of the requirements that gitlint enforces:

### Rule class requirements ###

- Rules **must** extend from  ```LineRule``` or ```CommitRule```
- Rule classes **must** have ```id``` and ```name``` string attributes. The ```options_spec``` is optional,
  but if set, it **must** be a list of gitlint Options.
- Rule classes **must** have a ```validate``` method. In case of a ```CommitRule```, ```validate```  **must** take a single ```commit``` parameter.
  In case of ```LineRule```, ```validate``` **must** take ```line``` and ```commit``` as first and second parameters.
- LineRule classes **must** have a ```target``` class attributes that is set to either ```CommitMessageTitle``` or ```CommitMessageBody```.
- User Rule id's **cannot** start with ```R```, ```T```, ```B``` or ```M``` as these rule ids are reserved for gitlint itself.
- Rules **should** have a case-insensitive unique id as only one rule can exist with a given id. While gitlint does not enforce this, having multiple rules with
  the same id might lead to unexpected or undeterministic behavior.

### extra-path requirements ###
- If  ```extra-path``` is a directory, it does **not** need to be a proper python package, i.e. it doesn't require an ```__init__.py``` file.
- Python files containing user-defined rules must have a ```.py``` extension. Files with a different extension will be ignored.
- The ```extra-path``` will be searched non-recursively, i.e. all rule classes must be present at the top level ```extra-path``` directory.
- User rule classes must be defined in the modules that are part of ```extra-path```, rules that are imported from outside the ```extra-path``` will be ignored.
