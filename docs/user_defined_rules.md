# User Defined Rules
*New in gitlint 0.8.0*

Gitlint supports the concept of user-defined rules: the ability for users
to write your own custom rules that are executed when gitlint is.

In a nutshell, you use ```--extra-path /home/joe/myextensions``` to point gitlint to a ```myextensions``` directory where it will search
for python files containing gitlint rule classes.

```bash
cat examples/commit-message-1 | gitlint --extra-path examples/
1: UC2 Body does not contain a 'Signed-Off-By Line'
# other violations were removed for brevity
```

This was the result of executing the SignedOffBy user-defined ```CommitRule``` that was found in the
[examples/gitlint/my_commit_rules.py](https://github.com/jorisroovers/gitlint/blob/master/examples/my_commit_rules.py) file:

```python
class SignedOffBy(CommitRule):
    """ This rule will enforce that each commit contains a "Signed-Off-By" line.
    We keep things simple here and just check whether the commit body contains a line that starts with "Signed-Off-By".
    """

    # A rule MUST have a human friendly name
    name = "body-requires-signed-off-by"

    # A rule MUST have an *unique* id, we recommend starting with UC (for User-defined Commit-rule).
    id = "UC2"

    def validate(self, commit):
        for line in commit.message.body:
            if line.startswith("Signed-Off-By"):
                return []

        return [RuleViolation(self.id, "Body does not contain a 'Signed-Off-By Line'", "", 1)]
```

As always ```--extra-path``` can also be set by adding it under the ```[general]``` section in your ```.gitlint``` file or using
one of the other ways to configure gitlint.  For more details, please refer to the [Configuration](configuration.md) page.


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
TODO

The classes below are examples of user-defined CommitRules. Commit rules are gitlint rules that
act on the entire commit at once. Once the rules are discovered, gitlint will automatically take care of applying them
to the entire commit. This happens exactly once per commit.

A CommitRule contrasts with a LineRule (see examples/my_line_rules.py) in that a commit rule is only applied once on
an entire commit. This allows commit rules to implement more complex checks that span multiple lines and/or checks
that should only be done once per gitlint run.

While every LineRule can be implemented as a CommitRule, it's usually easier and more concise to go with a LineRule if
that fits your needs.

## Violations ##
TODO
## Options ##
TODO


## Rule requirements ##

As long as you stick with simple scenarios that are similar to the sample User Defined rules (see the ```examples``` directory), gitlint
should be able to discover and execute your custom rules. If you want to do something more exotic however, you might run into some issues.

While the [rule finding source-code](https://github.com/jorisroovers/gitlint/blob/master/gitlint/user_rules.py) is the
ultimate source of truth, here are some of the requirements that gitlint enforces:

### Extra path requirements ###
- The ```extra-path``` option must point to a **directory**, not a file
- The ```extra-path``` directory does **not** need to be a proper python package, i.e. it doesn't require an ```__init__.py``` file.
- Python files containing user rules must have a ```.py``` extension. Files with a different extension will be ignored.
- The ```extra-path``` will be searched non-recursively, i.e. all rule classes must be present at the top level ```extra-path``` directory.
- User rule classes must be defined in the modules that are part of ```extra-path```, rules that are imported from outside the ```extra-path``` will be ignored.

### Rule class requirements ###

- Rules **must** extend from  ```LineRule``` or ```CommitRule```
- Rule classes **must** have ```id``` and ```name``` string attributes. The ```options_spec``` is optional, but if set, it **must** be a list.
- Rule classes **must** have a ```validate``` method. In case of a ```CommitRule```, ```validate```  *must* take a single ```commit``` parameter.
  In case of ```LineRule```, ```validate``` must take ```line``` and ```commit``` as first and second parameters.
- LineRule classes **must**
- User Rule id's **cannot** be of the form ```R[0-9]+```, ```T[0-9]+```, ```B[0-9]+``` or ```M[0-9]+``` as these rule ids are reserved for gitlint itself.
- Rule **should** have a unique id as only one rule can exist with a given id. While gitlint does not enforce this, the rule that will
  actually be chosen will be system specific.
