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

| Parameter | Type  | Description                                                                                                                                                      |
| --------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rule_id`   | `#!python str` | Rule's unique string id                                                                                                                                          |
| `message`   | `#!python str` | Short description of the violation                                                                                                                               |
| `content`   | `#!python str` | (optional) the violating part of commit or line                                                                                                                  |
| `line_nr`   | `#!python int` | (optional) line number in the commit message where the violation occurs. **Automatically set to the correct line number for `LineRule`s if not set explicitly.** |

A typical `validate(...)` implementation for a `CommitRule` would then be as follows:
```python
def validate(self, commit)
    for line_nr, line in commit.message.body:
        if "Jon Snow" in line:
            # Add 1 to the line_nr to offset the title which is on the first line
            violation_line_nr = line_nr + 1
            msg = "Commit message has the words 'Jon Snow' in it"
            return [RuleViolation(self.id, msg, line, violation_line_nr)]
    return []
```

The parameters of this `RuleViolation` can be directly mapped onto gitlint's output as follows:

![How Rule violations map to gitlint output](../../images/RuleViolation.png)
